import numpy as np
from mathutils import Euler

from . import abs_assignment
from m_CONST import POSE, COLLECTIONS
from blender.utils import objects
from utils import m_V


class BridgePose(abs_assignment.DataAssignment):
    def __init__(self):
        self.references = {
            # MEDIAPIPE DEFAULTS
            0:  POSE.nose,
            1:  POSE.left_eye_inner,
            2:  POSE.left_eye,
            3:  POSE.left_eye_outer,
            4:  POSE.right_eye_inner,
            5:  POSE.right_eye,
            6:  POSE.right_eye_outer,
            7:  POSE.left_ear,
            8:  POSE.right_ear,
            9:  POSE.mouth_left,
            10: POSE.mouth_right,
            11: POSE.left_shoulder,
            12: POSE.right_shoulder,
            13: POSE.left_elbow,
            14: POSE.right_elbow,
            15: POSE.left_wrist,
            16: POSE.right_wrist,
            17: POSE.left_pinky,
            18: POSE.right_pinky,
            19: POSE.left_index,
            20: POSE.right_index,
            21: POSE.left_thumb,
            22: POSE.right_thumb,
            23: POSE.left_hip,
            24: POSE.right_hip,
            25: POSE.left_knee,
            26: POSE.right_knee,
            27: POSE.left_ankle,
            28: POSE.right_ankle,
            29: POSE.left_heel,
            30: POSE.right_heel,
            31: POSE.left_foot_index,
            32: POSE.right_foot_index,

            # DRIVERS
            33: POSE.left_forearm_ik,
            34: POSE.right_forearm_ik,
            35: POSE.left_hand_ik,
            36: POSE.right_hand_ik,

            37: POSE.left_index_ik,
            38: POSE.right_index_ik,
            39: POSE.right_foot_ik,
            40: POSE.left_foot_ik,
            41: POSE.left_shin_ik,
            42: POSE.right_shin_ik,

            43: POSE.left_shoulder_ik,
            44: POSE.right_shoulder_ik,
            45: POSE.left_hip_ik,
            46: POSE.right_hip_ik
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
        self.col_name = COLLECTIONS.pose
        self.rotation_data = []
        self.scale_data = []

    def init_references(self):
        # default empties
        self.pose = objects.add_empties(self.references, 0.025)
        objects.add_list_to_collection(self.col_name, self.pose, self.driver_col)

        self.init_bpy_driver_obj(
            self.shoulder_center, self.pose, 0.01, POSE.shoulder_center, self.col_name, "SPHERE",
            [0, 0, 0])
        self.init_bpy_driver_obj(
            self.hip_center, self.pose, 0.01, POSE.hip_center, self.col_name, "SPHERE", [0, 0, 0])

    def init_data(self):
        self.rotation_data = []
        self.scale_data = []
        self.prepare_landmarks()
        self.shoulder_hip_location()
        self.shoulder_hip_rotation()
        self.average_rig_scale()

    def update(self):
        self.set_position()
        self.set_rotation()
        self.set_scale()

    def set_position(self):
        """Keyframe the position of input data."""
        try:
            self.translate(self.pose, self.data, self.frame)

        except IndexError:
            print("VALUE ERROR WHILE ASSIGNING POSE POSITION")

    def set_rotation(self):
        self.euler_rotate(self.pose, self.rotation_data, self.frame)
        pass

    def set_scale(self):
        self.scale(self.pose, self.scale_data, self.frame)

    def average_rig_scale(self):
        self.arm_chain_lengths()
        self.leg_chain_lengths()

    def leg_chain_lengths(self):
        """ every segment changes length individually during the tracking process """
        # 23: left_hip, 25: left_knee, 29: left_heel, 27: left_ankle
        left_hip_leg_length = m_V.get_vector_distance(self.hip_center.loc, self.data[23][1])
        left_upper_leg_length = m_V.get_vector_distance(self.data[23][1], self.data[25][1])
        left_lower_leg_length = m_V.get_vector_distance(self.data[25][1], self.data[27][1])
        left_foot_length = m_V.get_vector_distance(self.data[27][1], self.data[29][1])

        # 24: right_hip, 26: right_knee, 28: right_ankle, 30: right_heel
        right_hip_leg_length = m_V.get_vector_distance(self.hip_center.loc, self.data[24][1])
        right_upper_leg_length = m_V.get_vector_distance(self.data[24][1], self.data[26][1])
        right_lower_leg_length = m_V.get_vector_distance(self.data[26][1], self.data[28][1])
        right_foot_length = m_V.get_vector_distance(self.data[28][1], self.data[30][1])

        data = [
            [23, [1, 1, left_hip_leg_length]],
            [24, [1, 1, right_hip_leg_length]],
            [25, [1, 1, left_upper_leg_length]],
            [26, [1, 1, right_upper_leg_length]],
            [27, [1, 1, left_lower_leg_length]],
            [28, [1, 1, right_lower_leg_length]],
            [29, [1, 1, left_foot_length]],
            [30, [1, 1, right_foot_length]]
        ]

        for d in data:
            self.scale_data.append(d)

    def arm_chain_lengths(self):
        """ every segment changes length individually during the tracking process """

        # 11: left_shoulder, 13: left_elbow, 15: left_wrist, 19: left_index
        right_shoulder_arm_length = m_V.get_vector_distance(self.shoulder_center.loc, self.data[12][1])
        right_upper_arm_length = m_V.get_vector_distance(self.data[12][1], self.data[14][1])
        right_forearm_length = m_V.get_vector_distance(self.data[14][1], self.data[16][1])
        right_wrist_length = m_V.get_vector_distance(self.data[16][1], self.data[20][1])

        # 12: right_shoulder, 14: right_elbow, 16: right_wrist, 20: right_index
        left_shoulder_arm_length = m_V.get_vector_distance(self.shoulder_center.loc, self.data[11][1])
        left_upper_arm_length = m_V.get_vector_distance(self.data[11][1], self.data[13][1])
        left_forearm_length = m_V.get_vector_distance(self.data[13][1], self.data[15][1])
        left_wrist_length = m_V.get_vector_distance(self.data[15][1], self.data[19][1])

        data = [
            [11, [1, 1, left_shoulder_arm_length]],
            [12, [1, 1, right_shoulder_arm_length]],
            [13, [1, 1, left_upper_arm_length]],
            [14, [1, 1, right_upper_arm_length]],
            [15, [1, 1, left_forearm_length]],
            [16, [1, 1, right_forearm_length]],
            [19, [1, 1, left_wrist_length]],
            [20, [1, 1, right_wrist_length]]
        ]

        for d in data:
            self.scale_data.append(d)

    def torso_rotation(self):
        # approximate perpendicular points to origin
        hip_center = m_V.center_point(np.array(self.data[23][1]), np.array(self.data[24][1]))
        right_hip = np.array(self.data[24][1])
        shoulder_center = m_V.center_point(np.array(self.data[11][1]), np.array(self.data[12][1]))

        # generate triangle
        vertices = np.array(
            [self.data[23][1],
             self.data[24][1],
             shoulder_center])
        connections = np.array([[0, 1, 2]])

        # get normal from triangle
        normal, norm = m_V.create_normal_array(vertices, connections)

        # direction vectors from imaginary origin
        tangent = m_V.normalize(m_V.to_vector(hip_center, right_hip))
        normal = m_V.normalize(normal[0])
        binormal = m_V.normalize(m_V.to_vector(hip_center, shoulder_center))

        # generate matrix to decompose it and access quaternion rotation
        matrix = m_V.generate_matrix(tangent, binormal, normal)
        loc, quart, scale = m_V.decompose_matrix(matrix)

        offset = [-.5, 0, 0]
        euler = self.try_get_euler(quart, offset, self.hip_center.idx)
        euler = self.offset_euler(euler, offset)

        return euler

    def shoulder_rotation(self):
        # rotation from shoulder center to shoulder.R
        shoulder_center = m_V.center_point(self.data[11][1], self.data[12][1])
        shoulder_rotation = m_V.rotate_towards(shoulder_center, self.data[12][1], 'Z')

        # rotation from hip center to hip.R
        hip_center = m_V.center_point(self.data[23][1], self.data[24][1])
        hip_rotation = m_V.rotate_towards(hip_center, self.data[24][1], 'Z')

        # chance to offset result / rotation may not be keyframed
        offset = [0, 0, 0]
        shoulder_euler = self.try_get_euler(shoulder_rotation, offset, 7)
        shoulder_rot = self.offset_euler(shoulder_euler, offset)

        hip_euler = self.try_get_euler(hip_rotation, offset, 8)
        hip_rot = self.offset_euler(hip_euler, offset)

        # offset between hip & shoulder rot = real shoulder rot
        euler = Euler((shoulder_rot[0] - hip_rot[0],
                       shoulder_rot[1] - hip_rot[1],
                       shoulder_rot[2] - hip_rot[2]))

        return euler

    def shoulder_hip_rotation(self):
        """ Creates custom rotation data for driving the cgt_rig. """
        self.shoulder_center.rot = self.shoulder_rotation()
        self.hip_center.rot = self.torso_rotation()

        # setup data format
        data = [
            [self.shoulder_center.idx, self.shoulder_center.rot],
            [self.hip_center.idx, self.hip_center.rot]
        ]
        for d in data:
            self.rotation_data.append(d)

    def shoulder_hip_location(self):
        """ Appending custom location data for driving the cgt_rig. """
        self.shoulder_center.loc = m_V.center_point(self.data[11][1], self.data[12][1])
        self.data.append([self.shoulder_center.idx, self.shoulder_center.loc])

        self.hip_center.loc = m_V.center_point(self.data[23][1], self.data[24][1])
        self.data.append([self.hip_center.idx, self.hip_center.loc])

    def prepare_landmarks(self):
        """ setting face mesh position to approximate origin """
        self.data = [[idx, np.array([-lmrk[0], lmrk[2], -lmrk[1]])] for idx, lmrk in self.data]
