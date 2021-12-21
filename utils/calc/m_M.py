import numpy as np
from mathutils import Matrix, Quaternion


def generate_matrix(tangent: np.array, normal: np.array, binormal: np.array):
    """ returns matrix
    -> tangent = towards left and right [+X]
    -> normal = origin towards front [+Y]
    -> binormal = cross product of tanget and normal if +z1 [+Z] """
    return Matrix((
        [tangent[0],    tangent[1],     tangent[2],     0],
        [normal[0],     normal[1],      normal[2],      0],
        [binormal[0],   binormal[1],    binormal[2],    0],
        [0,             0,              0,              1],
    ))


def decompose_matrix(matrix: Matrix):
    """ returns loc, quaternion, scale """
    loc, quart, scale = matrix.decompose()
    quart.invert()
    return loc, quart, scale

