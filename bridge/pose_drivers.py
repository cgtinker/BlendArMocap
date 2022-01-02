import importlib

import numpy as np

from blender import objects
from bridge import abs_assignment
from utils import m_V, log
from mathutils import Euler

importlib.reload(abs_assignment)


class BridgePose(abs_assignment.DataAssignment):
    def __init__(self):
        self.references = {
            0:  "cgt_nose",
            1:  "cgt_left_eye_inner",
            2:  "cgt_left_eye",
            3:  "cgt_left_eye_outer",
            4:  "cgt_right_eye_inner",
            5:  "cgt_right_eye",
            6:  "cgt_right_eye_outer",
            7:  "cgt_left_ear",
            8:  "cgt_right_ear",
            9:  "cgt_mouth_left",
            10: "cgt_mouth_right",
            11: "cgt_left_shoulder",
            12: "cgt_right_shoulder",
            13: "cgt_left_elbow",
            14: "cgt_right_elbow",
            15: "cgt_left_wrist",
            16: "cgt_right_wrist",
            17: "cgt_left_pinky",
            18: "cgt_right_pinky",
            19: "cgt_left_index",
            20: "cgt_right_index",
            21: "cgt_left_thumb",
            22: "cgt_right_thumb",
            23: "cgt_left_hip",
            24: "cgt_right_hip",
            25: "cgt_left_knee",
            26: "cgt_right_knee",
            27: "cgt_left_ankle",
            28: "cgt_right_ankle",
            29: "cgt_left_heel",
            30: "cgt_right_heel",
            31: "cgt_left_foot_index",
            32: "cgt_right_foot_index"
        }

        self.pivot = abs_assignment.CustomData()
        self.shoulder_center = abs_assignment.CustomData()
        self.hip_center = abs_assignment.CustomData()

        self.pose = []
        self.col_name = "cgt_pose"
        self.rotation_data = []

    def init_references(self):
        # default empties
        self.pose = objects.add_empties(self.references, 0.025)
        objects.add_list_to_collection(self.col_name, self.pose, self.driver_col)

        self.init_bpy_driver_obj(
            self.pivot, self.pose, 0.025, "origin_rot", self.col_name, "SPHERE", [0, 0, 0])
        self.init_bpy_driver_obj(
            self.shoulder_center, self.pose, 0.01, "shoulder_center", self.col_name, "CUBE", [0, 0, 0])
        self.init_bpy_driver_obj(
            self.hip_center, self.pose, 0.01, "hip_center", self.col_name, "CUBE", [0, 0, 0])

    def init_data(self):
        self.rotation_data = []
        self.prepare_landmarks()
        self.shoulder_hip_location()
        self.shoulder_hip_rotation()
        self.arm_angles()
        self.leg_angles()

    def update(self):
        self.set_position()
        self.set_rotation()

    def set_position(self):
        """Keyframe the position of input data."""
        try:
            self.translate(self.pose, self.data, self.frame)

        except IndexError:
            log.logger.error("VALUE ERROR WHILE ASSIGNING POSE POSITION")

    def set_rotation(self):
        self.euler_rotate(self.pose, self.rotation_data, self.frame)

    def arm_angles(self):
        """ Get arm rotation data for driving the rig. """
        left_shoulder_rot = m_V.rotate_towards(self.data[11][1], self.data[13][1])
        right_shoulder_rot = m_V.rotate_towards(self.data[12][1], self.data[14][1])

        left_shoulder_rot = self.quart_to_euler_combat(left_shoulder_rot, 11)
        right_shoulder_rot = self.quart_to_euler_combat(right_shoulder_rot, 11)

        left_elbow_rot = m_V.rotate_towards(self.data[13][1], self.data[15][1])
        right_elbow_rot = m_V.rotate_towards(self.data[14][1], self.data[16][1])

        left_elbow_rot = self.quart_to_euler_combat(left_elbow_rot, 13)
        right_elbow_rot = self.quart_to_euler_combat(right_elbow_rot, 14)
        print("try set arm", self.frame)
        data = [
            [11, left_shoulder_rot],
            [12, right_shoulder_rot],
            [13, left_elbow_rot],
            [14, right_elbow_rot]
        ]

        for d in data:
            self.rotation_data.append(d)

    def leg_angles(self):
        """ Get leg rotation data for driving the rig. """
        left_hip_rot = m_V.rotate_towards(self.data[23][1], self.data[25][1])
        right_hip_rot = m_V.rotate_towards(self.data[24][1], self.data[26][1])

        left_hip_rot = self.quart_to_euler_combat(left_hip_rot, 23)
        right_hip_rot = self.quart_to_euler_combat(right_hip_rot, 24)

        left_knee_rot = m_V.angle_between(self.data[25][1], self.data[27][1])
        right_knee_rot = m_V.angle_between(self.data[26][1], self.data[28][1])

        data = [
            [23, left_hip_rot],
            [24, right_hip_rot],
            [25, Euler((left_knee_rot, 0, 0))],
            [26, Euler((right_knee_rot, 0, 0))]
        ]

        for d in data:
            self.rotation_data.append(d)

    def shoulder_hip_rotation(self):
        """ Creates custom rotation data for driving the rig. """
        # rotate custom shoulder center point from shoulder.R to shoulder.L
        self.shoulder_center.rot = m_V.rotate_towards(self.data[11][1], self.data[12][1])
        self.shoulder_center.rot = self.quart_to_euler_combat(self.shoulder_center.rot, self.shoulder_center.idx)

        # rotate custom hip center point from hip.R to hip.L
        self.hip_center.rot = m_V.rotate_towards(self.data[23][1], self.data[24][1])
        self.hip_center.rot = self.quart_to_euler_combat(self.hip_center.rot, self.hip_center.idx)

        # setup data format
        data = [
            [self.shoulder_center.idx, self.shoulder_center.rot],
            [self.hip_center.idx, self.hip_center.rot]
        ]

        for d in data:
            self.rotation_data.append(d)

    def shoulder_hip_location(self):
        """ Appending custom location data for driving the rig. """
        self.shoulder_center.loc = m_V.center_point(self.data[11][1], self.data[12][1])
        self.data.append([self.shoulder_center.idx, self.shoulder_center.loc])

        self.hip_center.loc = m_V.center_point(self.data[23][1], self.data[24][1])
        self.data.append([self.hip_center.idx, self.hip_center.loc])

    def prepare_landmarks(self):
        """ setting face mesh position to approximate origin """
        self.data = [[idx, np.array([-lmrk[0], lmrk[2], -lmrk[1]])] for idx, lmrk in self.data]
