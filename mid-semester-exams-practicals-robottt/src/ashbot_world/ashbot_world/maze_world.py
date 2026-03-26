"""
File: maze_world.py
Project: AshBot World
File Created: Sunday, 16th February 2025 5:03:29 PM
Author: nknab
Email: kojo.anyinam-boateng@alumni.ashesi.edu.gh
Version: 1.0
Brief: Generate a maze world in Gazebo
-----
Last Modified: Monday, 9th March 2026 4:08:59 PM
Modified By: nknab
-----
Copyright ©2025 nknab
"""

import xml.dom.minidom
from datetime import datetime
from math import pi
from os.path import join
from random import choices, sample
from typing import Any, Optional, Tuple
from uuid import uuid4

import yaml
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
    " ": (255, 255, 255),
    "PATH": (128, 128, 128),
}

PACKAGE_NAME = "ashbot_world"
TEMPLATE_DIR = "templates"
TEMPLATE = "maze.world.jinja"
WORLD_DIR = "worlds"

SELECTION_RATE = 0.35
CELL_SCALE_FACTOR = 1.5

GEM_TYPE_DISTRIBUTION = {
    "Red": 0.15,  # Hazard Gem
    "Green": 0.25,  # Epic Gem
    "Blue": 0.6,  # Standard Gem
}


def generate_gems(
    solution_path: list[tuple[int, int]], width: int, length: int
) -> list[dict[str, Any]]:
    """
    Generate the placement of gems in the maze.

    Parameters
    ----------
    solution_path : list[tuple[int, int]]
        The solution path of the maze.
    width : int
        The width of the maze.
    length : int
        The length of the maze.

    Returns
    -------
    list[dict[str, Any]]
        A list of dictionaries containing the colour and position of each gem.

    """
    num_gems = max(1, int(round(len(solution_path) * SELECTION_RATE)))
    step = max(1, len(solution_path) // (num_gems // 2))

    gem_samples = [
        sample(solution_path[i : i + step], 1)[0]
        for count, i in enumerate(range(1, len(solution_path) - 1, step))
        if count % 2 == 0
    ]

    coordinates = convert_to_center_coordinates(
        gem_samples,
        width,
        length,
    )

    gem_types = choices(
        list(GEM_TYPE_DISTRIBUTION.keys()),
        weights=list(GEM_TYPE_DISTRIBUTION.values()),
        k=len(coordinates),
    )

    return [
        {"colour": colour, "position": position}
        for colour, position in zip(gem_types, coordinates)
    ]


def generate_maze(
    width: int,
    length: int,
    vehicle_dim: Optional[Tuple[float, float]] = None,
    gems: bool = True,
    box_height: float = 0.4,
) -> None:
    """
    Generate a maze using the recursive backtracking algorithm.

    Parameters
    ----------
    width : int
        The width of the maze.

    length : int
        The length of the maze.

    vehicle_length : Optional[float], optional
        The length of the vehicle, by default None.

    gems : bool, optional
        Whether to place gems in the maze, by default True.

    box_height : float, optional
        The height of the boxes, by default 0.4.

    """

    cell_size = max(vehicle_dim) * CELL_SCALE_FACTOR if vehicle_dim else 0.5

    world_name = "maze_gems" if gems else "maze"

    maze = Maze(width, length)
    maze.generate_maze()

    solution_path = maze.solve_maze()[1:-1]
    walls = convert_to_center_coordinates(maze.get_walls(), width, length)

    maze = maze.get_maze()

    pkg_share = FindPackageShare(package=PACKAGE_NAME).find(PACKAGE_NAME)
    template_folder = join(pkg_share, TEMPLATE_DIR)
    world_folder = join(pkg_share, WORLD_DIR)

    world_filepath = join(world_folder, f"{world_name}.world")
    config_filepath = join(pkg_share, "config", f"{world_name}.yaml")

    env = Environment(loader=FileSystemLoader(template_folder))
    template = env.get_template(TEMPLATE)

    save_maze_to_image(maze, COLOUR_MAP, join(pkg_share, f"{world_name}.png"))
    save_maze_with_solution(
        maze, COLOUR_MAP, solution_path, join(pkg_share, f"{world_name}_solution.png")
    )

    context = {
        "world_name": world_name,
        "generation_date": datetime.now().strftime("%d-%m-%Y %H:%M:%S"),
        "generation_id": str(uuid4()),
        "box_height": box_height,
        "walls": walls,
        "cell_size": cell_size * 2 if gems else cell_size,
    }

    if gems:
        context["gems"] = generate_gems(solution_path, width, length)

    world = template.render(context)
    dom = xml.dom.minidom.parseString(world)
    pretty_arena = dom.toprettyxml(indent="  ")

    with open(world_filepath, "w", encoding="utf-8") as f:
        f.write("\n".join(line for line in pretty_arena.splitlines() if line.strip()))

    w_offset = vehicle_dim[0] / 2 if vehicle_dim is not None else cell_size / 2
    h_offset = vehicle_dim[1] / 2 if vehicle_dim is not None else cell_size / 2
    start = convert_to_center_coordinates([(1, 1)], width, length)
    end = convert_to_center_coordinates([(width - 2, length - 2)], width, length)

    config = {
        "generation_date": context["generation_date"],
        "generation_id": context["generation_id"],
        "start_coordinate": [
            (start[0][0] * context["cell_size"]) + w_offset,
            (start[0][1] * context["cell_size"]) + h_offset,
            -pi / 2 if maze[1][2] == " " else pi,
        ],
        "end_coordinate": [
            (end[0][0] * context["cell_size"]) + w_offset,
            (end[0][1] * context["cell_size"]) + h_offset,
        ],
    }

    with open(config_filepath, "w", encoding="utf-8") as config_file:
        yaml.dump(config, config_file)
