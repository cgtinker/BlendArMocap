import math as m
import numpy as np
from utils import log


def main():
    pass



# region elementary rotations
def euler_rotation(rx: float, ry: float, rz: float, order: str = 'XYZ', reversed_order: bool = False):
    """ returns a numpy matrix containing
    an euler rotation in given order"""
    look_up = {
        'X': rx,
        'Y': ry,
        'Z': rz
    }

    if reversed_order:
        order = order[::-1]

    try:
        rotation_matrices = [rotate_euler_axis(look_up[axis], axis) for axis in order]
    except KeyError:
        return None

    R = rotation_matrices[0] * rotation_matrices[1] * rotation_matrices[2]
    return R


def rotate_euler_axis(theta: float, axis: str):
    """ returns a numpy matrix containing
    an euler rotation on the given axis """
    rotation = None
    rotate_axis = {
        'X': euler_rx,
        'Y': euler_ry,
        'Z': euler_rz
    }

    try:
        rotation = rotate_axis[axis](theta)
    except KeyError:
        log.logger.error("given thetha is not valid")

    return rotation


# region elements
def euler_rx(theta: float):
    x = np.matrix([
        [1, 0, 0],
        [0, m.cos(theta), m.sin(theta)],
        [0, m.sin(theta), m.cos(theta)]
    ])
    return x


def euler_ry(theta: float):
    return np.matrix([
        [m.cos(theta), 0, m.sin(theta)],
        [0, 1, 0],
        [-m.sin(theta), 0, m.cos(theta)]
    ])


def euler_rz(theta: float):
    return np.matrix([
        [m.cos(theta), -m.sin(theta), 0],
        [m.sin(theta), 0, m.cos(theta)],
        [0, 0, 1],
    ])
# endregion
# endregion


if __name__ == "__main__":
    main()
