import math

from rover_navigation.math_utils import normalize_angle, shortest_angular_distance


def test_normalize_angle_wraps():
    assert math.isclose(normalize_angle(3.5), 3.5 - 2.0 * math.pi, rel_tol=1e-6)


def test_shortest_distance_across_pi_boundary():
    start = math.radians(179.0)
    end = math.radians(-179.0)
    delta = shortest_angular_distance(start, end)
    assert abs(delta) < math.radians(5.0)
