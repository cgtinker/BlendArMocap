import math

import numpy as np
from mathutils import Euler, Matrix, Vector

from utils import log


# region vector utils
def vector_length(vector: np.array):
    """ returns the length of a given vector. """
    vec = np.sum(vector ** 2)
    return np.sqrt(vec)
    # return np.linalg.norm(vector, ord=1)


def to_vector(origin: np.array, destination: np.array):
    """ returns vector from origin to destination. """
    return destination - origin


def normalize(vector: np.array):
    """ returns the unit vector of the vector. """
    return vector / np.linalg.norm(vector)


def vector_length_2d(v1, v2, del_axis: str = ""):
    """ returns the magnitude between two vectors. """
    remove_axis([v1, v2], del_axis)
    vec = to_vector(v1, v2)
    return vector_length(vec)


def get_vector_distance(v1, v2):
    """ return distance between two points. """
    return math.sqrt(
        (v2[0] - v1[0]) ** 2 +
        (v2[1] - v1[1]) ** 2 +
        (v2[2] - v1[2]) ** 2
    )


# region axis helper
def remove_axis(vectors, *args):
    """ delete one axis to calculate 2d intersection point """
    axis = {
        "X": 0,
        "Y": 1,
        "Z": 2
    }
    res = []
    for arg in args:
        try:
            for vec in vectors:
                res.append([np.delete(vec, axis[arg]) for arg in args])
        except KeyError:
            log.logger.warning(arg, "AXIS NOT AVAILABLE")

    return res


def null_axis(vectors, *args):
    """ delete one axis to calculate 2d intersection point """
    axis = {
        "X": 0,
        "Y": 1,
        "Z": 2
    }
    res = []

    for vec in vectors:
        tmp = [v for v in vec]
        for arg in args:
            tmp[axis[arg]] = 0
        res.append(tmp)

    return res


# endregion
# endregion


# region angle and rotation
# region angle
def angle_between(v1: np.array, v2: np.array):
    """ Returns the angle in radians between vectors. """
    v1, v2 = normalize(v1), normalize(v2)
    dot = np.dot(v1, v2)
    limited_dot = np.clip(dot, -1.0, 1.0)
    return np.arccos(limited_dot)


# TODO: remove and replace with numpy
def rotate_towards(origin, destination, track='Z', up='Y'):
    """ returns rotation from an origin to a destination. """
    vec = Vector((destination - origin))
    vec = vec.normalized()
    quart = vec.to_track_quat(track, up)
    return quart


# region joint
def joint_angles(vertices, joints):
    angles = [joint_angle(vertices, joint) for joint in joints]
    return angles


def joint_angle(vertices, joint):
    """ returns angle between joint. """
    angle = angle_between(
        to_vector(vertices[joint[0]], vertices[joint[1]]),
        to_vector(vertices[joint[1]], vertices[joint[2]]))
    return angle


# endregion
# endregion
# endregion


# region point
def center_point(p1: np.array, p2: np.array):
    """ return center point from two given points. """
    return (p1 + p2) / 2


# endregion


# region intersection
# https://web.archive.org/web/20111108065352/https://www.cs.mun.ca/%7Erod/2500/notes/numpy-arrays/numpy-arrays.html
def intersection_2d_vectors(origin_p1: np.array, target_p1: np.array,
                            origin_p2: np.array, target_p2: np.array, del_axis: str, ):
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
        np.delete(point, axis[del_axis])

    intersection = seg_intersect(origin_p1, target_p1, origin_p2, target_p2)
    return intersection


def rotate_seg(a):
    """ rotate by 90° """
    b = np.empty_like(a)
    b[0] = -a[1]
    b[1] = a[0]
    return b


def seg_intersect(a1, a2, b1, b2):
    """ line segment a given by endpoints a1, a2
        line segment b given by endpoints b1, b2 """
    dist_a = a2 - a1
    dist_b = b2 - b1
    dist_p = a1 - b1
    dist_ap = rotate_seg(dist_a)
    denom = np.dot(dist_ap, dist_b)
    num = np.dot(dist_ap, dist_p)
    return (num / denom.astype(float)) * dist_b + b1


# endregion


# region normal from face
# https://github.com/vladmandic/human/pull/91
def create_normal_array(vertices: np.array, faces: np.array):
    """return array of normals per triangle. each vertex triplet
    requires a face triplet
    vertices = [[[1, 1, 0],[0,1,0],[0,0,0]], []...] faces = [[0, 1, 2], []...]"""
    norm = np.zeros(vertices.shape, dtype=vertices.dtype)
    # indexed view into the vertex array
    # using the array of three indices for triangles
    tris = vertices[faces]
    # Calculate the normal for all the triangles,
    # by taking the cross product of the vectors v1-v0, and v2-v0 in each triangle
    normals = np.cross(tris[::, 1] - tris[::, 0], tris[::, 2] - tris[::, 0])
    return normals, norm


# endregion


# region matrix
# todo: remove and replace with numpy
# http://renderdan.blogspot.com/2006/05/rotation-matrix-from-axis-vectors.html
def generate_matrix(tangent: np.array, normal: np.array, binormal: np.array):
    """ returns matrix
    -> tangent = towards left and right [+X]
    -> normal = origin towards front [+Y]
    -> binormal = cross product of tanget and normal if +z1 [+Z] """
    return Matrix((
        [tangent[0], tangent[1], tangent[2], 0],
        [normal[0], normal[1], normal[2], 0],
        [binormal[0], binormal[1], binormal[2], 0],
        [0, 0, 0, 1],
    ))


def main():
    # testing for further updates
    tangent = np.array([0, 1, 0])
    normal = np.array([0, 4, 1])
    binormal = np.array([1, 0, 0])

    matrix = np_genenerate_matrix(tangent, normal, binormal)
    loc, rot_matrix, scale = np_decompose_matrix(matrix)
    print(matrix)
    print("\nloc\n", loc, "\nrot\n", rot_matrix, "\nsca\n", scale)


def np_genenerate_matrix(tangent: np.array, normal: np.array, binormal: np.array):
    """ generate a numpy matrix at loc [0, 0, 0]. """
    matrix = np.array([
        [tangent[0], tangent[1], tangent[2], 0],
        [normal[0], normal[1], normal[2], 0],
        [binormal[0], binormal[1], binormal[2], 0],
        [0, 0, 0, 1]])
    return matrix


def np_decompose_matrix(matrix):
    # location -> last column of matrix
    loc = matrix[:3, 3:4]

    # scale -> length of the first the column vectors
    sx = vector_length(matrix[:3, 0:1])
    sy = vector_length(matrix[:3, 1:2])
    sz = vector_length(matrix[:3, 2:3])
    sca = np.array([sx, sy, sz])

    # rotation -> divide first three column vectors by the scaling factors
    # todo: fix for negative scale and apply shear
    c1 = matrix[:3, 0:1] / sx
    c2 = matrix[:3, 1:2] / sy
    c3 = matrix[:3, 2:3] / sz

    # recreate matrix (loc = [0, 0, 0]
    rotation_matrix = np.array([np.append(col, [v]) for col, v in
                                [[c1, 0], [c2, 0], [c3, 0], [loc, 1]]])

    # todo: quaternion from rotation matrix
    return loc, rotation_matrix, sca


def decompose_matrix(matrix: Matrix):
    """ returns loc, quaternion, scale """
    loc, quart, scale = matrix.decompose()
    quart.invert()
    return loc, quart, scale


def to_euler(quart, combat=Euler(), space='XYZ', ):
    euler = quart.to_euler(space, combat)
    return euler


# endregion


if __name__ == "__main__":
    main()
