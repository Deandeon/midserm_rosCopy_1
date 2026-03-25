import math

from maze_navigation.math_utils import normalize_angle, shortest_angular_distance


def test_normalize_angle_wraps():
    assert math.isclose(normalize_angle(4.0), 4.0 - 2.0 * math.pi)


def test_shortest_angular_distance_basic():
    result = shortest_angular_distance(0.0, math.pi / 2.0)
    assert math.isclose(result, math.pi / 2.0)
