import numpy as np
from utils import log


def intersection_2d_vectors(origin_p1: np.array, target_p1: np.array,
                            origin_p2: np.array, target_p2: np.array, ignore_axis: str, ):
    """ returns intersection point tuple
    intersect 2d vector from origin to destination
    with targeted 2d vector.
    requires to ignore an axis."""
    axis = {
        "X": 0,
        "Y": 1,
        "Z": 2
    }

    # ignore one axis to calculate 2d intersection point
    for point in [origin_p1, target_p1, origin_p2, target_p2]:
        np.delete(point, axis[ignore_axis])

    return seg_intersect(origin_p1, target_p1, origin_p2, target_p2)


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
        '': [0, 0, 0]
    }

    vector = np.array([0, 0, 0])
    for arg in args:
        try:
            vector += np.array(target[arg])
        except KeyError:
            print("err")
            log.logger.error(arg, "AXIS NOT AVAILABLE")

    return vector


def perp(a):
    # rotating by 180
    b = np.empty_like(a)
    b[0] = -a[1]
    b[1] = a[0]
    return b


# line segment a given by endpoints a1, a2
# line segment b given by endpoints b1, b2
# https://web.archive.org/web/20111108065352/https://www.cs.mun.ca/%7Erod/2500/notes/numpy-arrays/numpy-arrays.html
def seg_intersect(a1, a2, b1, b2):
    dist_a = a2 - a1
    dist_b = b2 - b1
    dist_p = a1 - b1
    dist_ap = perp(dist_a)
    denom = np.dot(dist_ap, dist_b)
    num = np.dot(dist_ap, dist_p)
    return (num / denom.astype(float)) * dist_b + b1


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
            log.logger.warning(arg, "AXIS NOT AVAILABLE")
    return vec