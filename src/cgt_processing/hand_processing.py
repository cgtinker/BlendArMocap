'''
Copyright (C) cgtinker, cgtinker.com, hello@cgtinker.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

from math import degrees

import numpy as np
from mathutils import Euler

from . import processor_interface
from ..cgt_bridge import bpy_hand_bridge
from ..cgt_utils import m_V


class HandProcessor(processor_interface.DataProcessor):
    fingers = [
        [1, 5],  # thumb
        [5, 9],  # index finger
        [9, 13],  # middle finger
        [13, 17],  # ring finger
        [17, 21],  # pinky
    ]

    # for printing
    max_values = [-155] * 20
    min_values = [155] * 20

    #  position and joint angle
    left_hand_data, right_hand_data = None, None
    left_angles, right_angles = None, None

    # bridge to blender engine
    bridge = None
    frame = 0

    def __init__(self, bridge=bpy_hand_bridge.BpyHandBridge):
        self.bridge = bridge

    def init_references(self):
        """ Generates objects for mapping. """
        self.bridge = self.bridge("HAND")

    def init_data(self):
        """ Process and map received data from mediapipe before key-framing. """
        # prepare landmarks
        # TODO: check for holistic hand input (left / right) hand - consider to preprocess
        z_left_hand_data = self.set_global_origin(self.data[0])
        z_right_hand_data = self.set_global_origin(self.data[1])

        # get finger angles
        self.left_angles = self.finger_angles(z_left_hand_data)
        self.right_angles = self.finger_angles(z_right_hand_data)

        # get hand rotation
        left_hand_rot = self.global_hand_rotation(z_left_hand_data, 0, "L")
        if left_hand_rot is not None:
            self.left_angles.append(left_hand_rot)

        right_hand_rot = self.global_hand_rotation(z_right_hand_data, 100, "R")  # offset for euler combat
        if right_hand_rot is not None:
            self.right_angles.append(right_hand_rot)

        self.left_hand_data = self.set_global_origin(self.data[0])
        self.right_hand_data = self.set_global_origin(self.data[1])

    def init_print(self):
        """ processed printing doesnt support mathutils rotation functions. """
        self.left_hand_data = self.set_global_origin(self.data[0])
        self.right_hand_data = self.set_global_origin(self.data[1])

    def update(self):
        """ Applies gathered data to references. """
        locations = [[], []]
        angles = [[], []]
        if self.right_hand_data is not None:
            if not self.has_duplicated_results(self.right_hand_data, "hand", 0):
                locations[1] = self.right_hand_data
                angles[1] = self.right_angles

        if self.left_hand_data is not None:
            if not self.has_duplicated_results(self.left_hand_data, "hand", 1):
                locations[0] = self.left_hand_data
                angles[0] = self.left_angles

        self.bridge.set_position(locations, self.frame)
        self.bridge.set_rotation(angles, self.frame)

    def get_processed_data(self):
        """ Returns the processed data """
        position_data = [self.left_hand_data, self.right_hand_data]
        rotation_data = [self.left_angles, self.right_angles]
        scale_data = None
        return position_data, rotation_data, scale_data, self.frame, self.has_duplicated_results(self.data)

    def finger_angles(self, hand):
        """ Get finger x-angles from landmarks. """
        if hand == []:
            return None

        x_angles = self.get_x_angles(hand)
        z_angles = self.get_z_angles(hand)

        data = []
        for idx in range(0, 20):
            if x_angles[idx] != 0 or z_angles[idx] != 0:
                joint_angle = [idx, Euler((x_angles[idx], 0, z_angles[idx]))]
                data.append(joint_angle)

        # self.print_angle_matrix(z_angles)
        return data

    def print_angle_matrix(self, angles):
        """ Prints the finger angles and their min and max values during a session
            helps to find proper mapping values """
        deg = [degrees(d) for d in angles]

        # current
        for finger in self.fingers:
            cu = [[idx, self.min_values[idx], deg[idx], self.max_values[idx]] for idx in
                  range(finger[0], finger[1] - 1)]
            print(cu)

        # min max values
        for idx, d in enumerate(deg):
            if d > self.max_values[idx]:
                self.max_values[idx] = d
            if d < self.min_values[idx]:
                self.min_values[idx] = d

    def get_z_angles(self, hand):
        """ Project finger mcps on a vector between index and pinky mcp.
            Create circles around the mcps circles facing in the direction of vectors depending on the palm.
            Searching for the closest point on the circle to the fingers dip and calculate the angle.
            Thumb gets projected on a plane between thumb mcp, index mcp and wrist to calculate the z-angle.
        """
        data = [0] * 20
        joints = np.array([[0, 1, 2]])

        def calculate_thumb_angle():
            # create plane to project thumb mcp & pip on plane
            plane = np.array([np.array([0, 0, 0]), hand[1][1], hand[5][1]])
            thumb_proj = [m_V.project_vec_on_plane(plane, joints, p)
                          for p in [hand[1][1], hand[5][1], hand[2][1]]]

            # vectors to calculate angle
            thumb_vecs = [m_V.to_vector(tp[0], tp[1]) for tp in [
                [thumb_proj[0], thumb_proj[1]],
                [thumb_proj[0], thumb_proj[2]]]]

            return m_V.angle_between(np.array(thumb_vecs[0]), np.array(thumb_vecs[1]))

        data[1] = calculate_thumb_angle()

        # calculate other finger angles
        tangent = m_V.to_vector(np.array(hand[5][1]), np.array(hand[17][1]))
        # get pips, mcps and their dists (mcps projected on tangent)
        mcps = [m_V.project_point_on_vector(
            np.array(hand[finger[0]][1]), np.array(hand[5][1]), np.array(hand[17][1]))
            for finger in self.fingers[1:]]
        pips = [np.array(hand[finger[1] - 2][1]) for finger in self.fingers[1:]]
        dists = [m_V.get_vector_distance(mcps[i], pips[i]) for i in range(0, 4)]

        # circle direction vectors related to the hand to calc angles
        pinky_vec = m_V.to_vector(np.array(hand[0][1]), np.array(hand[17][1]))
        thumb_vec = m_V.to_vector(np.array(hand[1][1]), np.array(hand[5][1]))
        dirs = [pinky_vec, pinky_vec, thumb_vec, thumb_vec]

        points = 20
        for i in range(0, 4):
            # create a circle around tangent in target dir
            # and find the closest point from circle to pip
            circle = m_V.create_circle_around_vector(tangent, mcps[i], dists[i], points, dirs[i])
            closest = m_V.get_closest_idx(pips[i], circle)

            # angle between the closest point on circle to mcp and pip to mcp vectors
            mcp_pip = m_V.to_vector(mcps[i], pips[i])
            mcp_closest = m_V.to_vector(mcps[i], circle[closest])

            # expand the arr of the circle to avoid index errors
            # form a triangle on the circle facing the closet point to the pip
            expanded_circle = circle + circle + circle
            a = expanded_circle[closest + points + 6]
            b = expanded_circle[closest + points - 6]

            # calculate the normal from the triangle
            plane = np.array([a, circle[closest], b])
            normal = m_V.normal_from_plane(plane)
            normal = m_V.normalize(normal)

            # get the distance from the triangle to the pip
            dist = m_V.distance_from_plane(pips[i], normal, circle[closest])

            # check if the finger angle should be pos or neg based on the dist
            angle = m_V.angle_between(np.array(mcp_pip), np.array(mcp_closest))
            if dist < 0:
                angle = -angle
            else:
                pass

            data[self.fingers[i + 1][0]] = angle

        return data

    def get_x_angles(self, hand):
        """ Get finger x angle by calculating the angle between each finger joint """
        # add the wrist as origin to all fingers (0, 0, 0)
        fingers = [[hand[idx][1] for idx in range(finger[0], finger[1])] for finger in self.fingers]
        wrist_origin = np.array([0, 0, 0])
        fingers = [np.array([wrist_origin] + finger) for finger in fingers]
        joints = np.array([[0, 1, 2]])

        # straighten fingers by plane projection
        for idx, finger in enumerate(fingers):
            plane = np.array([np.array([0, 0, 0]), finger[1], finger[4]])
            f = [m_V.project_vec_on_plane(plane, joints, p) for p in finger]
            fingers[idx] = f

        # setup joints to calc finger angles
        x_joints = [[0, 1, 2], [1, 2, 3], [2, 3, 4]]
        x_finger_angles = [m_V.joint_angles(finger, x_joints) for finger in fingers]

        data = [0] * 20
        for idx, angles in enumerate(x_finger_angles):
            if angles is None:
                break

            # iter over every finger joint and calc angle
            mcp, tip = self.fingers[idx]
            for angle_idx, finger_idx in enumerate(range(mcp, tip - 1)):
                data[finger_idx] = angles[angle_idx]

        return data

    def global_hand_rotation(self, hand, combat_idx_offset=0, orientation="R"):
        """ Calculates approximate hand rotation by generating
            a matrix using the palm as approximate triangle. """
        if hand == []:
            return None

        # default hand rotation for a rigify A-Pose rig,
        if orientation == "R":
            rotation = [-60, 60, 0]
        else:
            rotation = [-60, -60, 0]

        # rotate points before calculating the rotation
        rotated_points = [m_V.rotate_point_euler(np.array(hand[idx][1]), rotation) for idx in [1, 5, 13]]

        # setup vectors to create an matrix
        tangent = m_V.normalize(m_V.to_vector(
            rotated_points[0],
            rotated_points[1]
        ))
        binormal = m_V.normalize(m_V.to_vector(
            rotated_points[1],
            rotated_points[2]
        ))
        normal = m_V.normalize(np.cross(binormal, tangent))

        # rotation from matrix
        matrix = m_V.generate_matrix(normal, tangent, binormal)
        loc, quart, sca = m_V.decompose_matrix(matrix)
        euler = self.try_get_euler(quart, offset=[0, 0, 0], prev_rot_idx=combat_idx_offset)
        hand_rotation = ([0, euler])
        return hand_rotation

    def landmarks_to_hands(self, left_hand, right_hand): # hand_data):
        """ Determines to which hand the landmark data belongs """
        left_hand = self.set_global_origin(left_hand)
        right_hand = self.set_global_origin(right_hand)

        return left_hand, right_hand

    @staticmethod
    def set_global_origin(data):
        """ Sets the wrist to (0, 0, 0) while the wrist is the origin of the fingers.
            Changes the x-y-z order to match blenders coordinate system. """
        if data is None:
            # todo: skip this
            return data

        if len(data) > 0:
            print("FIDX", data[0][0][1])
            if np.isnan(np.sum(data[0][0][1])):
                print("IS NAN")
                data = [[idx, np.array([-landmark[0], landmark[2], -landmark[1]])] for idx, landmark in data[0]]
                return data
            data = [[idx, np.array([-landmark[0], landmark[2], -landmark[1]])] for idx, landmark in data[0]]
            data = [[idx, landmark - data[0][1]] for idx, landmark in data]
        return data
