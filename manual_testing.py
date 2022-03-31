import os
import sys
from mathutils import Vector
from math import degrees
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
import math
import mathutils

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
    [1, 5],  # thumb
    [5, 9],  # index finger
    [9, 13],  # middle finger
    [13, 17],  # ring finger
    [17, 21],  # pinky
]


def m_hand():
    _fingers = get_fingers()
    _hand = get_hand(".R")
    hand = [[idx, vertex.location, vertex] for idx, vertex in enumerate(_hand)]
    return hand


def get_hand(_dir=".L"):
    names = [name + _dir for name in finger_names]
    return [objects.get_object_by_name(name) for name in names]


def get_fingers(_dir=".L"):
    names = []
    for finger in fingers:
        vertex_names = [finger_names[idx] + _dir for idx in range(finger[0], finger[1] - 1)]
        for name in vertex_names:
            names.append(name)
    return [objects.get_object_by_name(name) for name in names]


def get_y_angles(hand):
    joints = np.array([[0, 1, 2]])
    data = [0] * 20
    plane_tris = [
        [1, 5],  # thumb
        [5, 9],  # index
        [9, 13],  # middle
        [13, 17],  # ring -> basically [13, 9]
        [17, 21]  # pinky -> [17, 13]
    ]

    # palm based plane
    plane = np.array([
        np.array([0, 0, 0]),
        hand[5][1],
        hand[17][1]
    ])

    # project proximal phalanges on plane based on surrounding metacarpals
    for idx, finger in enumerate(fingers):
        if idx == 0:
            # thumb based plane
            plane = np.array([
                np.array([0, 0, 0]),
                hand[1][1],
                hand[5][1]
            ])

        ### PROJ MCP ###
        proj_mcp = m_V.project_vec_on_plane(plane, joints, hand[finger[0]][1])
        hand[finger[0]][2].location = proj_mcp

        ### PROJ PIP ON PLANE###
        pip = hand[finger[0] + 1]
        proj_pip = m_V.project_vec_on_plane(plane, joints, np.array(pip[1]))
        pip[2].location = proj_pip
        proj_pip = np.array(pip[1])
        # vector to chain mcps
        if idx < 3:
            proj_mcp_b = m_V.project_vec_on_plane(plane, joints, hand[finger[1]][1])
            mcp_vector = m_V.to_vector(proj_mcp, proj_mcp_b)
            mcp_vector = m_V.to_vector(hand[finger[1]][1], hand[finger[0]][1])

        else:
            # changing vector direction?
            proj_mcp_b = m_V.project_vec_on_plane(plane, joints, hand[fingers[idx - 1][0]][1])
            mcp_vector = m_V.to_vector(proj_mcp, proj_mcp_b)
            mcp_vector = m_V.to_vector(hand[fingers[idx - 1][0]][1], hand[fingers[idx - 1][1]][1])

        # mcp to pip vec
        tar_vec = m_V.to_vector(np.array(proj_mcp), np.array(proj_pip))
        angle = m_V.angle_between(np.array(tar_vec), np.array(mcp_vector))
        t = m_V.angle_between(proj_mcp, proj_mcp_b)
        # angle = angle/fac
        # angle = m_V.angle_between(np.array(proj_mcp), np.array(proj_pip))
        if angle is None:
            break

        data[finger[0]] = (degrees(angle))

    angles = [int(d) for d in data if d != 0]
    print(angles)
    # return data


def project_mcps_on_vec(hand):
    # project mcps to vector from index to pinky mcp
    mcps = []
    for idx, finger in enumerate(fingers[1:]):
        mcp = hand[finger[0]][1]
        proj_mcp = m_V.project_point_on_vector(
            np.array(mcp), np.array(hand[5][1]), np.array(hand[17][1])
        )

        hand[finger[0]][2].location = proj_mcp
        mcps.append(proj_mcp)

    return mcps


def get_mcp_pip_dist(hand, mcps):
    dists = []
    for idx, finger in enumerate(fingers[1:]):
        mcp = mcps[idx]
        pip = np.array(hand[finger[0] + 1][1])
        dist = m_V.get_vector_distance(mcp, pip)
        dists.append(dist)
    return dists


def get_pips(hand):
    pips = []
    for idx, finger in enumerate(fingers[1:]):
        pip = np.array(hand[finger[0] + 1][1])
        pips.append(pip)
    return pips


def create_angled_circle(c, r, angle=90, points=10, axis="x"):
    rot = angle
    thetha = np.linspace(0, 2 * np.pi, points)

    y = np.cos(thetha)
    z = np.sin(thetha)

    # set angle
    phi = np.deg2rad(rot)
    # apply angle

    x = c[0] + y * np.cos(phi) * r
    y = c[1] + y * np.sin(phi) * r
    z = c[2] + z * r

    circle = [[x[i], y[i], z[i]] for i in range(0, len(x))]

    for i, point in enumerate(circle):
        # print(i, point)
        ob = objects.add_empty(0.001, f"test{i}")
        res = point
        ob.location = res


def circle():
    r = .01
    thetha = np.linspace(0, 2 * np.pi, 10)
    origin = np.array([.01, 0, 0])

    for i, t in enumerate(thetha):
        y = np.cos(t) * r
        z = np.sin(t) * r
        ob = objects.add_empty(0.001, f"test{i}")
        ob.location = [0, y, z]


def circle_along_UV(center=np.array([0, 0, 0]),
                    U=np.array([0, 1, 0]),
                    V=np.array([0, 0, 1]),
                    r=0.025,
                    points=21):
    # C(t) = c + r*U*cos(t)+e*V*sin(t)
    thetha = np.linspace(0, np.pi * 2, points)

    U = m_V.normalize(U)
    V = m_V.normalize(V)

    cos_t = np.cos(thetha)
    sin_t = np.sin(thetha)

    x = center[0] + r * U[0] * cos_t + r * V[0] * sin_t
    y = center[1] + r * U[1] * cos_t + r * V[1] * sin_t
    z = center[2] + r * U[2] * cos_t + r * V[2] * sin_t

    circle = [[x[i], y[i], z[i]] for i in range(0, len(x))]

    for i, point in enumerate(circle):
        # print(i, point)
        ob = objects.add_empty(0.0025, f"test{i}", "SPHERE")
        ob.location = point

    return circle


def create_circle_around_vector(vector, center, radius, points, normal=np.array([1, 1, 1])):
    # q = p1->p2 moved to origin
    Q = vector
    # https://stackoverflow.com/questions/36760771/how-to-calculate-a-circle-perpendicular-to-a-vector
    # vectors U & V mutally perpendicular and perpendicular to Q
    # (Qx, Qy, Qz)·(Ux, Uy, Uz) = Qx·Ux + Qy·Uy + Qz·Uz = Qx·-Qy/Qx + Qy·1 + Qz·0 = -Qy + Qy + 0 = 0
    if Q[0] != 0:
        # U = np.array([-Q[1]/Q[0], 1, 0])
        U = np.array([-Q[1] / Q[0], 1, 0])
    elif Q[1] != 0:
        U = np.array([0, -Q[2] / Q[1], 1])
    else:
        U = np.array([1, 0, -Q[0] / Q[2]])

    # The cross product of two vectors is perpendicular to both
    # (Vx, Vy, Vz) = (Qx, Qy, Qz)×(Ux, Uy, Uz) = (Qy×Uz - Qz×Uy, Qz×Ux - Qx×Uz, Qx×Uy - Qy×Ux)
    U = normal
    V = np.cross(Q, U)
    circle = circle_along_UV(center, U, V, radius, points)
    return circle


def get_closest_point(target, points):
    distances = np.sum((points - target) ** 2, axis=1)
    closest = points[np.argmin(distances)]
    return closest


def get_y_angles_circular(hand):
    joints = np.array([[0, 1, 2]])
    data = [0] * 20

    # create plane to calc thumb angle
    plane = np.array([np.array([0, 0, 0]), hand[1][1], hand[5][1]])

    # project mcps & pip on plane
    proj_mcp = m_V.project_vec_on_plane(plane, joints, hand[1][1])
    proj_mcp_b = m_V.project_vec_on_plane(plane, joints, hand[5][1])
    proj_pip = m_V.project_vec_on_plane(plane, joints, np.array(hand[2][1]))

    # vectors for angle calculation
    mcp_vector = m_V.to_vector(proj_mcp, proj_mcp_b)
    tar_vec = m_V.to_vector(np.array(proj_mcp), np.array(proj_pip))

    # thumb angle
    angle = m_V.angle_between(np.array(tar_vec), np.array(mcp_vector))
    data[1] = angle


    # calculate other finger angles
    tangent = m_V.to_vector(np.array(hand[5][1]), np.array(hand[17][1]))
    tangent_dist = m_V.vector_length(tangent)

    # get pips, mcps and their dists (mcps projected on tangent)
    mcps = [m_V.project_point_on_vector(
        np.array(hand[finger[0]][1]), np.array(hand[5][1]), np.array(hand[17][1]))
        for finger in fingers[1:]]
    # mcps = [np.array(hand[finger[0]][1]) for finger in fingers[1:]]
    pips = [np.array(hand[finger[1] -2][1]) for finger in fingers[1:]]
    dists = [m_V.get_vector_distance(mcps[i], pips[i]) for i in range(0, 4)]

    # circle direction vectors related to the hand to calc angles
    pinky_vec =  m_V.to_vector(np.array(hand[0][1]), np.array(hand[17][1]))
    thumb_vec = m_V.to_vector(np.array(hand[1][1]), np.array(hand[5][1]))
    dirs = [pinky_vec, pinky_vec, thumb_vec, thumb_vec]

    # circle around tangent
    for i in range(0, 4):
        circle = create_circle_around_vector(tangent, mcps[i], dists[i], 20, dirs[i])
        closest = get_closest_point(pips[i], circle)
        # angle between closest point on circle to mcp and pip to mcp vectors
        mcp_pip = m_V.to_vector(mcps[i], pips[i])
        mcp_facing = m_V.to_vector(mcps[i], closest)
        angle = m_V.angle_between(np.array(mcp_pip), np.array(mcp_facing))
        data[fingers[i + 1][0]] = angle

    angles = [int(degrees(d)) for d in data if d != 0]
    print(angles)
    # return data


def do_stuff():
    hand = m_hand()
    tangent = m_V.to_vector(np.array(hand[5][1]), np.array(hand[17][1]))
    normal, n = m_V.create_normal_array(
        np.array([np.array(hand[0][1]), np.array(hand[5][1]), np.array(hand[17][1])]),
        np.array([[0, 1, 2]])
    )
    normal = m_V.normalize(-normal[0])

    center = (np.array(hand[5][1]) + np.array(hand[17][1])) / 2
    dir = m_V.to_vector(center, np.array([0, 0, 0]))
    dir = m_V.to_vector(np.array(hand[1][1]), np.array(hand[5][1]))
    dir = m_V.normalize(dir)

    mcps = [m_V.project_point_on_vector(
        np.array(hand[finger[0]][1]), np.array(hand[5][1]), np.array(hand[17][1]))
        for finger in fingers[1:]]

    pips = [np.array(hand[finger[0] + 1][1]) for finger in fingers[1:]]
    dists = get_mcp_pip_dist(hand, mcps)
    circle = create_circle_around_vector(tangent, mcps[0], dists[0], 20, dir)
    get_closest_point(pips[1], circle)
    print("done")


def main():
    hand = m_hand()
    # frames to target:
    print("\n\nREMEASURING")
    measure_container = [
        ["\nfront open", [0, 40, 80]],
        ["front straight", [120, 150, 180]],
        ["front closed", [190, 210, 240]],

        ["\nback open", [420, 440, 460]],
        ["back straight", [490, 510, 530]],
        ["back closed", [300, 350, 390]]
    ]

    for container in measure_container:
        print(container[0])
        for frame in container[1]:
            bpy.context.scene.frame_set(frame)
            get_y_angles_circular(hand)


if __name__ == "__main__":
    main()
    # get_y_angles_circular(m_hand())
    #do_stuff()