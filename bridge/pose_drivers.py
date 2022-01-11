import importlib
from math import pi

import numpy as np
from mathutils import Euler

from blender import objects
from bridge import abs_assignment
from utils import m_V, log

importlib.reload(abs_assignment)


class BridgePose(abs_assignment.DataAssignment):
    def __init__(self):
        self.references = {
            # MEDIAPIPE DEFAULTS
            0: "cgt_nose",
            1: "cgt_left_eye_inner",
            2: "cgt_left_eye",
            3: "cgt_left_eye_outer",
            4: "cgt_right_eye_inner",
            5: "cgt_right_eye",
            6: "cgt_right_eye_outer",
            7: "cgt_left_ear",
            8: "cgt_right_ear",
            9: "cgt_mouth_left",
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
            32: "cgt_right_foot_index",

            # DRIVERS
            33: "cgt_left_forearm_ik_driver",
            34: "cgt_right_forearm_ik_driver",
            35: "cgt_left_hand_ik_driver",
            36: "cgt_right_hand_ik_driver",
            37: "cgt_right_foot_ik_driver",
            38: "cgt_left_foot_ik_driver",
            39: "cgt_left_shin_ik_driver",
            40: "cgt_right_shin_ik_driver"
        }

        self.arms = [
            [12, 17],  # right arm
            [11, 16]  # left arm_z
        ]

        self.legs = [
            [24, 29],  # right leg
            [23, 30]  # left leg
        ]

        self.shoulder_center = abs_assignment.CustomData()
        self.hip_center = abs_assignment.CustomData()

        self.pose = []
        self.col_name = "cgt_pose"
        self.rotation_data = []
        self.scale_data = []

    def init_references(self):
        # default empties
        self.pose = objects.add_empties(self.references, 0.025)
        objects.add_list_to_collection(self.col_name, self.pose, self.driver_col)

        self.init_bpy_driver_obj(
            self.shoulder_center, self.pose, 0.01, "shoulder_center", self.col_name, "SPHERE", [0, 0, 0])
        self.init_bpy_driver_obj(
            self.hip_center, self.pose, 0.01, "hip_center", self.col_name, "SPHERE", [0, 0, 0])

        self.init_bpy_driver_obj(
            self.hip_center, self.pose, 0.01, "", self.col_name, "SPHERE", [0, 0, 0])
        self.init_bpy_driver_obj(
            self.shoulder_center, self.pose, 0.01, "", self.col_name, "SPHERE", [0, 0, 0])
        self.init_bpy_driver_obj(
            self.hip_center, self.pose, 0.01, "", self.col_name, "SPHERE", [0, 0, 0])

    def init_data(self):
        self.rotation_data = []
        self.scale_data = []
        self.prepare_landmarks()

        self.average_rig_scale()
        self.shoulder_hip_location()
        self.shoulder_hip_rotation()

    def average_rig_scale(self):
        avg_arm_length = self.get_joint_chain_length(self.arms)
        self.scale_data.append([11, [1, 1, avg_arm_length]])
        self.scale_data.append([12, [1, 1, avg_arm_length]])

        avg_leg_lengths = self.get_joint_chain_length(self.legs)
        self.scale_data.append([23, [1, 1, avg_leg_lengths]])
        self.scale_data.append([24, [1, 1, avg_leg_lengths]])

    def get_joint_chain_length(self, joint_chain):
        """ get length of joint chain """
        avg_lengths = []
        for vertices in joint_chain:
            # setup a joint [0, 0+2] for the arm vertices to get vector distances
            joints = [[self.data[vertex][1], self.data[vertex + 2][1]] for vertex in range(vertices[0], vertices[1] - 2, 2)]
            vertex_lengths = [m_V.get_vector_distance(joint[0], joint[1]) for joint in joints]

            # average lengths
            avg_length = sum(vertex_lengths) / len(vertex_lengths)
            avg_lengths.append(avg_length)
        avg_length = sum(avg_lengths) / len(avg_lengths)
        return avg_length

    def update(self):
        self.set_position()
        self.set_rotation()
        self.set_scale()

    def set_position(self):
        """Keyframe the position of input data."""
        try:
            self.translate(self.pose, self.data, self.frame)

        except IndexError:
            log.logger.error("VALUE ERROR WHILE ASSIGNING POSE POSITION")

    def set_rotation(self):
        self.euler_rotate(self.pose, self.rotation_data, self.frame)
        pass

    def set_scale(self):
        self.scale(self.pose, self.scale_data, self.frame)

    @staticmethod
    def offset_euler(euler, offset: []):
        rotation = Euler((
            euler[0] + pi * offset[0],
            euler[1] + pi * offset[1],
            euler[2] + pi * offset[2],
        ))
        return rotation

    def try_get_euler(self, quart_rotation, offset: [], prev_rot_idx: int):
        print("try get euler", offset, prev_rot_idx, self.frame)
        try:
            m_rot = m_V.to_euler(
                quart_rotation,

                Euler((
                    self.prev_rotation[prev_rot_idx][0] + pi * offset[0],
                    self.prev_rotation[prev_rot_idx][1] + pi * offset[1],
                    self.prev_rotation[prev_rot_idx][2] + pi * offset[2],
                ))
            )
        except KeyError:
            m_rot = m_V.to_euler(quart_rotation)
        print(m_rot)
        return m_rot

    # todo use above method
    def shoulder_hip_rotation(self):
        """ Creates custom rotation data for driving the rig. """
        # rotate custom shoulder center point from shoulder.R to shoulder.L
        self.shoulder_center.rot = m_V.rotate_towards(self.data[11][1], self.data[12][1])
        # rotate custom hip center point from hip.R to hip.L
        self.hip_center.rot = m_V.rotate_towards(self.data[23][1], self.data[24][1])

        # todo: add combat euler
        self.hip_center.rot = m_V.to_euler(self.hip_center.rot)
        self.shoulder_center.rot = m_V.to_euler(self.shoulder_center.rot)

        # offset rotations
        r = self.shoulder_center.rot
        self.shoulder_center.rot = Euler((r[0], r[1], r[2]))
        self.shoulder_center.rot = Euler((r[0] - pi * .5, r[1], r[2] - pi * .5))

        r = self.hip_center.rot
        self.hip_center.rot = Euler((r[0], r[1], r[2]))
        self.hip_center.rot = Euler((r[0] - pi * .5, r[1], r[2] - pi * .5))

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
