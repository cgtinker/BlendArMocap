import numpy as np


def angle_between(v1: np.array, v2: np.array):
    """ Returns the angle in radians between vectors. """
    v1, v2 = normalize(v1), normalize(v2)
    dot = np.dot(v1, v2)
    limited_dot = np.clip(dot, -1.0, 1.0)
    return np.arccos(limited_dot)


def quaternion_angle_origin_to_destination(origin: np.array, destination: np.array):
    """ Returns quaternion rotation from point towards target. """
    point = normalize(origin)
    axis_vector = normalize(np.cross(origin, destination))
    angle = -angle_between(point, destination)
    return rot_angle_to_quaternion(angle, axis_vector)


def vector_length(vector: np.array):
    """ returns the length of a given vector. """
    vec = np.sum(vector ** 2)
    return np.sqrt(vec)


def to_vector(destination: np.array, origin: np.array):
    """ returns vector from origin to destination. """
    return destination - origin


def normalize(vector: np.array):
    """ Returns the unit vector of the vector. """
    return vector / np.linalg.norm(vector)


def rot_angle_to_quaternion(theta: float, vector: np.array):
    """ converts angle theta in radians to quaternion (w, x, y, z). """
    w = np.cos(theta / 2)
    xyz = np.sin(theta / 2) * vector
    return np.hstack((w, xyz))
