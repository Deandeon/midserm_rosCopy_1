"""
File: utils.py
Project: AshBot World
File Created: Sunday, 16th February 2025 5:59:06 PM
Author: nknab
Email: kojo.anyinam-boateng@alumni.ashesi.edu.gh
Version: 1.0
Brief: Utility functions for the maze.
-----
Last Modified: Sunday, 16th February 2025 6:09:54 PM
Modified By: nknab
-----
Copyright ©2025 nknab
"""

import itertools

from PIL import Image, ImageDraw


def draw_maze(
    maze: list[list[str]],
    colour_map: dict[str, tuple[int, int, int]],
    draw: ImageDraw.ImageDraw,
    cell_size: int,
    solution_path=None,
) -> None:
    """
    Draw the maze on an image.

    Parameters
    ----------
    maze : list[list[str]]
        The maze.

    colour_map : dict[str, tuple[int, int, int]]
        The colour map for the maze.

    draw : ImageDraw.ImageDraw
        The ImageDraw object.

    cell_size : int
        The size of each cell.

    solution_path : list[tuple[int, int]]
        The solution path of the maze.

    """

    height, width = len(maze), len(maze[0])

    for y, x in itertools.product(range(height), range(width)):
        colour = colour_map.get(maze[y][x], (255, 255, 255))
        if (x, y) == (1, 1):
            colour = (255, 255, 0)  # Yellow for the starting cell
        elif (x, y) in [
            (width - 1, height - 2),
            (width - 2, height - 1),
            (width - 1, height - 1),
        ]:
            colour = (0, 0, 255)  # Blue for the end cell

        draw.rectangle(
            [x * cell_size, y * cell_size, (x + 1) * cell_size, (y + 1) * cell_size],
            fill=colour,
        )

    if solution_path:
        for x, y in solution_path:
            if (x, y) != (1, 1):
                draw.rectangle(
                    [
                        x * cell_size,
                        y * cell_size,
                        (x + 1) * cell_size,
                        (y + 1) * cell_size,
                    ],
                    fill=colour_map["PATH"],
                )


def save_maze_to_image(
    maze: list[list[str]],
    colour_map: dict[str, tuple[int, int, int]],
    filename: str,
    cell_size: int = 50,
) -> None:
    """
    Save the maze to an image.

    Parameters
    ----------
    maze : list[list[str]]
        The maze.

    colour_map : dict[str, tuple[int, int, int]]
        The colour map for the maze.

    filename : str
        The filename to save the image.

    cell_size : int
        The size of each cell.

    """
    height, width = len(maze), len(maze[0])
    img = Image.new("RGB", (width * cell_size, height * cell_size), "white")
    draw = ImageDraw.Draw(img)
    draw_maze(maze, colour_map, draw, cell_size)
    img.save(filename)


def save_maze_with_solution(
    maze: list[list[str]],
    colour_map: dict[str, tuple[int, int, int]],
    solution_path: list[tuple[int, int]],
    filename: str,
    cell_size: int = 50,
) -> None:
    """
    Save the maze with the solution path to an image.

    Parameters
    ----------
    maze : list[list[str]]
        The maze.

    colour_map : dict[str, tuple[int, int, int]]
        The colour map for the maze.

    solution_path : list[tuple[int, int]]
        The solution path of the maze.

    filename : str
        The filename to save the image.

    cell_size : int
        The size of each cell.

    """
    height, width = len(maze), len(maze[0])
    img = Image.new("RGB", (width * cell_size, height * cell_size), "white")
    draw = ImageDraw.Draw(img)
    draw_maze(maze, colour_map, draw, cell_size, solution_path)
    img.save(filename)

def convert_to_center_coordinates(
    boxes: list[tuple[int, int]], maze_width: int, maze_height: int
) -> list[tuple[int, int]]:
    """
    Convert the box coordinates to center coordinates.

    Parameters
    ----------
    boxes : list[tuple[int, int]]
        The box coordinates.

    maze_width : int
        The width of the maze.

    maze_height : int
        The height of the maze.

    Returns
    -------
    list[tuple[int, int]]
        The center coordinates of the boxes.

    """

    center_x, center_y = maze_width // 2, maze_height // 2
    return [(center_y - y, center_x - x) for x, y in boxes]