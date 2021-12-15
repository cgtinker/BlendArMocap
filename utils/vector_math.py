import math
from mathutils import Vector


def get_vector_distance(v_a, v_b):
    return math.sqrt(
            (v_b[0] - v_a[0]) ** 2 +
            (v_b[1] - v_a[1]) ** 2 +
            (v_b[2] - v_a[2]) ** 2
        )


def get_center_point(p_a, p_b):
    center_point = Vector((
            (p_a[0] + p_b[0]) / 2,
            (p_a[1] + p_b[1]) / 2,
            (p_a[2] + p_b[2]) / 2,
        ))
    return center_point


def get_vector_from_points(p_a, p_b):
    """ p_a = origin; p_b = destination """
    vec = Vector((
        p_b[0] - p_a[0],
        p_b[1] - p_a[1],
        p_b[2] - p_a[2]
    ))
    return vec


def get_angle_between_vectors(v_a, v_b):
    return v_a.angle(v_b)