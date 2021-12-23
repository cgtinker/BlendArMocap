from blender import objects
from bridge import abs_assignment
import numpy as np
import importlib
from utils import m_V, log

importlib.reload(abs_assignment)


class BridgePose(abs_assignment.DataAssignment):
    def __init__(self, mode='realtime'):
        self.references = {
            0: "nose",
            1: "left_eye_inner",
            2: "left_eye",
            3: "left_eye_outer",
            4: "right_eye_inner",
            5: "right_eye",
            6: "right_eye_outer",
            7: "left_ear",
            8: "right_ear",
            9: "mouth_left",
            10: "mouth_right",
            11: "left_shoulder",
            12: "right_shoulder",
            13: "left_elbow",
            14: "right_elbow",
            15: "left_wrist",
            16: "right_wrist",
            17: "left_pinky",
            18: "right_pinky",
            19: "left_index",
            20: "right_index",
            21: "left_thumb",
            22: "right_thumb",
            23: "left_hip",
            24: "right_hip",
            25: "left_knee",
            26: "right_knee",
            27: "left_ankle",
            28: "right_ankle",
            29: "left_heel",
            30: "right_heel",
            31: "left_foot_index",
            32: "right_foot_index"
        }

        self.pose = []
        self.col_name = "Pose"
        self.rotation_data = None
        # todo: add state
        if mode != 'debug':
            self.init_references()

    def init_references(self):
        # default empties
        self.pose = objects.add_empties(self.references, 0.025)

        # custom mapping references
        self.pose.append(objects.add_empty(size=0.025, name="shoulder_center"))
        self.pose.append(objects.add_empty(size=0.025, name="hip_center"))
        self.pose.append(objects.add_empty(size=0.05, name="origin"))

        # set parent for further mapping
        objects.set_parents(self.pose[len(self.pose)-1], self.pose[:len(self.pose)-1])
        objects.add_list_to_collection(self.col_name, self.pose)

    def init_data(self):
        self.prepare_landmarks()
        self.shoulder_hip_location()
        self.shoulder_hip_rotation()

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

    def shoulder_hip_rotation(self):
        """ Creates custom rotation data for driving the rig. """
        # rotate custom shoulder center point from shoulder.R to shoulder.L
        shoulder_rot = m_V.rotate_towards(self.data[11][1], self.data[12][1])
        shoulder_rot = self.quart_to_euler_combat(shoulder_rot, 0)

        # rotate custom hip center point from hip.R to hip.L
        hip_rot = m_V.rotate_towards(self.data[23][1], self.data[24][1])
        hip_rot = self.quart_to_euler_combat(hip_rot, 1)

        # setup data format
        data = [
            [33, [shoulder_rot[0], shoulder_rot[1], shoulder_rot[2]]],
            [34, [hip_rot[0], hip_rot[1], hip_rot[2]]]
        ]

        self.rotation_data = data

    def shoulder_hip_location(self):
        """ Appending custom location data for driving the rig. """
        shoulder_center = m_V.center_point(self.data[11][1], self.data[12][1])
        self.data.append([33, [shoulder_center[0], shoulder_center[1], shoulder_center[2]]])

        hip_center = m_V.center_point(self.data[23][1], self.data[24][1])
        self.data.append([34, [hip_center[0], hip_center[1], hip_center[2]]])

    def prepare_landmarks(self):
        """ setting face mesh position to approximate origin """
        self.data = [[idx, np.array([-lmrk[0], lmrk[2], -lmrk[1]])] for idx, lmrk in self.data]
