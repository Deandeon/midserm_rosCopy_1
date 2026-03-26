"""
File: guided_maze.py
Project: AshBot World
File Created: Sunday, 26th January 2025 5:50:10 PM
Author: nknab
Email: kojo.anyinam-boateng@alumni.ashesi.edu.gh
Version: 1.0
Brief: A module for generating a guided maze.
-----
Last Modified: Monday, 9th March 2026 3:41:18 PM
Modified By: nknab
-----
Copyright ©2025 nknab
"""

import xml.dom.minidom
from datetime import datetime
from os.path import join
from uuid import uuid4

from jinja2 import Environment, FileSystemLoader
from launch_ros.substitutions import FindPackageShare

from ashbot_world.maze import Maze
from ashbot_world.utils import (
    convert_to_center_coordinates,
    save_maze_to_image,
    save_maze_with_solution,
)

COLOUR_MAP = {
    "#": (0, 0, 0),
    "L": (0, 255, 0),
    "R": (255, 0, 0),
    " ": (255, 255, 255),
    "PATH": (128, 128, 128),
}

PACKAGE_NAME = "ashbot_world"
TEMPLATE_DIR = "templates"
TEMPLATE = "guided_maze.world.jinja"
WORLD_DIR = "worlds"


def get_box_placement(
    maze: list[list[str]], solution_path: list[tuple[int, int]]
) -> tuple[list[list[str]], list[tuple[int, int]], list[tuple[int, int]]]:
    """
    Get the placement of the red and green boxes in the maze.

    Parameters
    ----------
    maze : list[list[str]]
        The maze.

    solution_path : list[tuple[int, int]]
        The solution of the maze

    Returns
    -------
    tuple[list[list[str]], list[tuple[int, int]], list[tuple[int, int]]]
        The maze with the boxes placed, the red boxes, and the green boxes.

    """

    directions, red_boxes, green_boxes = [], [], []
    direction_map = {
        ("right", "up"): ("R", -1, -1),
        ("right", "down"): ("L", -1, 1),
        ("left", "up"): ("L", 1, -1),
        ("left", "down"): ("R", 1, 1),
        ("up", "right"): ("L", 1, 1),
        ("up", "left"): ("R", -1, 1),
        ("down", "right"): ("R", 1, -1),
        ("down", "left"): ("L", -1, -1),
    }

    for i in range(1, len(solution_path)):
        dx, dy = (
            solution_path[i][0] - solution_path[i - 1][0],
            solution_path[i][1] - solution_path[i - 1][1],
        )
        directions.append(
            "right" if dx == 1 else "left" if dx == -1 else "down" if dy == 1 else "up"
        )

        if len(directions) > 1:
            prev_direction, current_direction = directions[-2], directions[-1]
            if (current_direction, prev_direction) in direction_map:
                box_type, offset_x, offset_y = direction_map[
                    (current_direction, prev_direction)
                ]
                x, y = solution_path[i][0] + offset_x, solution_path[i][1] + offset_y
                maze[y][x] = box_type
                (red_boxes if box_type == "R" else green_boxes).append((x, y))

    return maze, red_boxes, green_boxes


def generate_maze(
    width: int, length: int, cell_size: float = 0.5, box_height: float = 0.4
) -> None:
    """
    Generate a maze using the recursive backtracking algorithm.

    Parameters
    ----------
    width : int
        The width of the maze.

    length : int
        The length of the maze.

    """
    maze = Maze(width, length)
    maze.generate_maze()

    solution_path = maze.solve_maze()
    maze = maze.get_maze()

    maze, red_boxes, green_boxes = get_box_placement(maze, solution_path)

    red_boxes = convert_to_center_coordinates(red_boxes, width, length)
    green_boxes = convert_to_center_coordinates(green_boxes, width, length)

    blue_boxes = convert_to_center_coordinates(
        [(width - 2, length - 1), (width - 1, length - 2), (width - 1, length - 1)],
        width,
        length,
    )

    pkg_share = FindPackageShare(package=PACKAGE_NAME).find(PACKAGE_NAME)
    template_folder = join(pkg_share, TEMPLATE_DIR)
    world_folder = join(pkg_share, WORLD_DIR)

    world_filepath = join(world_folder, TEMPLATE.replace(".jinja", ""))

    env = Environment(loader=FileSystemLoader(template_folder))
    template = env.get_template(TEMPLATE)

    save_maze_to_image(maze, COLOUR_MAP, join(pkg_share, "guided_maze.png"))
    save_maze_with_solution(
        maze, COLOUR_MAP, solution_path, join(pkg_share, "guided_maze_solution.png")
    )

    context = {
        "world_name": "guided maze",
        "generation_date": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        "generation_id": str(uuid4()),
        "box_height": box_height,
        "cell_size": cell_size,
        "red_boxes": red_boxes,
        "green_boxes": green_boxes,
        "blue_boxes": blue_boxes,
    }

    world = template.render(context)
    dom = xml.dom.minidom.parseString(world)
    pretty_arena = dom.toprettyxml(indent="  ")

    with open(world_filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(line for line in pretty_arena.splitlines() if line.strip()))
