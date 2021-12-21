import numpy as np
import math
from mathutils import Vector
from time import time
from utils import log


def main():
    p = np.array([0, 4, 2])
    quat= quaternion_from_point(p, target_vector('X'))
    print(quat)


# region quaternion
def rot_angle_to_quaternion(theta, vector):
    """ converts angle theta in radians to quaternion (w, x, y, z) """
    w = np.cos(theta / 2)
    xyz = np.sin(theta / 2) * vector
    return np.hstack((w, xyz))


def angle_between(vec_a, vec_b):
    """ Returns the angle in radians between vectors. """
    v1, v2 = normalize_vector(vec_a), normalize_vector(vec_b)
    dot = np.dot(v1, v2)
    limited_dot = np.clip(dot, -1.0, 1.0)
    return np.arccos(limited_dot)


def quaternion_from_point(point, target):
    """ Returns quaternion rotation from point towards target. """
    point = normalize_vector(point)
    axis_vector = normalize_vector(np.cross(point, target))
    angle = -angle_between(point, target)
    return rot_angle_to_quaternion(angle, axis_vector)

# endregion


# region location
def center_point(p_a, p_b):
    """ return center point from two given points. """
    return (p_a + p_b) / 2


def vector_from_points(origin, dest):
    """ returns vector from two given points. """
    return dest-origin
# endregion


# region utils
def normalize_vector(vec):
    """ Returns the unit vector of the vector. """
    return vec / np.linalg.norm(vec)


def old_normalize_vector(vec):
    """ returns a normalized vector. 50% slower than above. """
    magnitude = vector_length(vec)
    return vec/magnitude


def vector_length(vec):
    """ returns the length of a given vector. """
    vec = np.sum(vec**2)
    return np.sqrt(vec)


def ignore_axis(vec, *args):
    """ null axis ['X', 'Y', 'Z'] of a given vector. """
    ignore = {
        'X': 0,
        'Y': 1,
        'Z': 2,
    }

    for arg in args:
        try:
            vec[ignore[arg]] = 0
        except KeyError:
            log.logger.error(arg, "AXIS NOT AVAILABLE")
    return vec


def target_vector(*args):
    """ Returns a vector for targeting ['X', 'Y', 'Z', '-X', '-Y', '-Z'] axis.
    Vector can target multiple axis. """
    target = {
        'X': [1, 0, 0],
        'Y': [0, 1, 0],
        'Z': [0, 0, 1],
        '-X': [-1, 0, 0],
        '-Y': [0, -1, 0],
        '-Z': [0, 0, -1],
    }

    vector = np.array([0, 0, 0])
    for arg in args:
        try:
            vector += np.array(target[arg])
        except KeyError:
            print("err")
            log.logger.error(arg, "AXIS NOT AVAILABLE")

    return vector
# endregion


if __name__ == '__main__':
    main()
