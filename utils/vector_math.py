import math
from mathutils import Vector


# region location
def get_center_point(p_a, p_b):
    """ return center point from two given points. """
    center_point = Vector((
        (p_a[0] + p_b[0]) / 2,
        (p_a[1] + p_b[1]) / 2,
        (p_a[2] + p_b[2]) / 2,
    ))
    return center_point


def get_vector_from_points(origin, dest):
    """ returns vector from two points. """
    vec = Vector((
        dest[0] - origin[0],
        dest[1] - origin[1],
        dest[2] - origin[2]
    ))
    return vec
# endregion


# region utils
def get_direction_vec(vec_a, vec_b):
    """ returns normalized direction vector. """
    return Vector((
        vec_a[0] - vec_b[0],
        vec_a[1] - vec_b[1],
        vec_a[2] - vec_b[2]
    ))


def get_vector_distance(p_a, p_b):
    """ return distance between two points. """
    return math.sqrt(
        (p_b[0] - p_a[0]) ** 2 +
        (p_b[1] - p_a[1]) ** 2 +
        (p_b[2] - p_a[2]) ** 2
    )


def get_vector_length(vec):
    """ returns the length of a given vector. """
    return math.sqrt(
        vec[0] ** 2 + vec[1] ** 2 + vec[2] ** 2
    )


def normalize_vector(vec):
    """ returns a normalized vector. """
    magnitude = get_vector_length(vec)
    return Vector((
        vec[0] / magnitude,
        vec[1] / magnitude,
        vec[2] / magnitude
    ))
# endregion


# region Rotation
def rotate_towards(origin, destination):
    """ returns rotation from an origin to a destination. """
    dir_vec = get_direction_vec(origin, destination)
    dir_vec = dir_vec.normalized()
    quart = dir_vec.to_track_quat('Z', 'Y')
    euler = quart.to_euler('XYZ')
    return euler


def get_angle_between_vectors(vec_a, vec_b):
    """ returns angle between two vectors. """
    return vec_a.angle(vec_b)
# endregion
