import os
import sys

import bpy

# getting access to the current dir - necessary to access blender file location
blend_dir = os.path.dirname(bpy.data.filepath)
if blend_dir not in sys.path:
    sys.path.append(blend_dir)
# append sys path to dir
main_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'module')
sys.path.append(main_dir)

from src.cgt_blender.utils import objects
from src.cgt_utils import m_V
import numpy as np

finger_names = ["CGT_WRIST",
                "CGT_THUMB_CMC",
                "CGT_THUMB_MCP",
                "CGT_THUMP_IP",
                "CGT_THUMB_TIP",
                "CGT_INDEX_FINGER_MCP",
                "CGT_INDEX_FINGER_PIP",
                "CGT_INDEX_FINGER_DIP",
                "CGT_INDEX_FINGER_TIP",
                "CGT_MIDDLE_FINGER_MCP",
                "CGT_MIDDLE_FINGER_PIP",
                "CGT_MIDDLE_FINGER_DIP",
                "CGT_MIDDLE_FINGER_TIP",
                "CGT_RING_FINGER_MCP",
                "CGT_RING_FINGER_PIP",
                "CGT_RING_FINGER_DIP",
                "CGT_RING_FINGER_TIP",
                "CGT_PINKY_MCP",
                "CGT_PINKY_PIP",
                "CGT_PINKY_DIP",
                "CGT_PINKY_TIP"]

fingers = [
    [5, 9],  # index finger
    [9, 13],  # middle finger
    [13, 17],  # ring finger
    [17, 21],  # pinky
    [1, 5]  # thumb
]


def get_finger_objs():
    names = [name + ".L" for name in finger_names]
    return [objects.get_object_by_name(name) for name in names]


def project_vec_on_vec(target, destination):
    # project vector u on vector v
    v_norm = m_V.vector_length(target)
    # find dot product using np.dot()
    proj_of_u_on_v = (np.dot(destination, target) / v_norm ** 2) * target
    return proj_of_u_on_v


def project_vec_on_plane(triangle, faces, vec):
    normals, norm = m_V.create_normal_array(np.array(triangle), np.array([faces]))
    projection = project_vec_from_normal(normals[0], np.array(vec))
    return projection


def project_vec_from_normal(normal, vector):
    """The projection of a vector v
    onto a plane is calculated by subtracting the component of u
    which is orthogonal to the plane from u"""
    n_norm = m_V.vector_length(normal)
    proj_of_vec_on_norm = (np.dot(vector, normal) / n_norm ** 2) * normal
    # this is the projection of the vector on normal of the input plane
    return vector - proj_of_vec_on_norm


def main():
    objs = get_finger_objs()
    loc = [ob.location for ob in objs]

    projection = project_vec_on_plane([loc[0], loc[9], loc[5]], [0, 1, 2], np.array(loc[6])-np.array(loc[5]))
    angle = m_V.angle_between(np.array(projection), np.array(loc[9]) - np.array(loc[0]))
    print(angle)


if __name__ == "__main__":
    main()
