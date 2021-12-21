import numpy as np


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