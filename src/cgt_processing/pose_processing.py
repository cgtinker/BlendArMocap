import numpy as np
from mathutils import Euler

from . import processor_interface
from ..cgt_bridge import bpy_pose_bridge
from ..cgt_utils import m_V


class PoseProcessor(processor_interface.DataProcessor):
    arms = [
        [12, 17],  # right arm
        [11, 16]  # left arm
    ]

    legs = [
        [24, 29],  # right leg
        [23, 30]  # left leg
    ]

    shoulder_center = None
    hip_center = None

    rotation_data = []
    scale_data = []

    def __init__(self, bridge=bpy_pose_bridge.BpyPoseBridge):
        self.bridge = bridge

    def init_references(self):
        """ Create references for mapping. """
        self.bridge = self.bridge("POSE")
        _pose, self.shoulder_center, self.hip_center = self.bridge.get_instances()

    def init_data(self):
        """ Init and process the input data. """
        self.rotation_data = []
        self.scale_data = []
        self.prepare_landmarks()
        self.shoulder_hip_location()
        self.shoulder_hip_rotation()
        self.average_rig_scale()

    def init_print(self):
        """ processed printing doesnt support mathutils rotation functions. """
        self.scale_data = []
        self.prepare_landmarks()
        self.shoulder_hip_location()
        self.average_rig_scale()

    def update(self):
        """ Apply the processed data to references. """
        if self.has_duplicated_results(self.data):
            return

        self.bridge.set_position(self.data, self.frame)
        self.bridge.set_rotation(self.rotation_data, self.frame)
        self.bridge.set_scale(self.scale_data, self.frame)

    def get_processed_data(self):
        """ Returns the processed data """
        return self.data, self.rotation_data, self.scale_data, self.frame, self.has_duplicated_results(self.data)

    def average_rig_scale(self):
        """ Get arm and leg chain lengths as those may vary each frame. """
        self.arm_chain_lengths()
        self.leg_chain_lengths()

    def leg_chain_lengths(self):
        """ Every segment changes length individually during the tracking process """
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
        """ Every segment changes length individually during the tracking process """

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
        """ Calculating the torso rotation based on a plane which
            forms a triangle connecting hips and the shoulder center. """
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
        return euler

    def shoulder_rotation(self):
        """ getting shoulder and hip rotation by rotating
            the center points to left / right shoulder and hip. """
        # TODO: use own rotate towards (requires testing)
        # rotation from shoulder center to shoulder.R
        shoulder_center = m_V.center_point(self.data[11][1], self.data[12][1])
        shoulder_rotation = m_V.rotate_towards(shoulder_center, self.data[12][1], 'Z')

        # rotation from hip center to hip.R
        hip_center = m_V.center_point(self.data[23][1], self.data[24][1])
        hip_rotation = m_V.rotate_towards(hip_center, self.data[24][1], 'Z')

        # chance to offset result / rotation may not be keyframed
        offset = [0, 0, 0]
        shoulder_rot = self.try_get_euler(shoulder_rotation, offset, 7)
        hip_rot = self.try_get_euler(hip_rotation, offset, 8)

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
        self.data = [[idx, np.array([-landmark[0], landmark[2], -landmark[1]])] for idx, landmark in self.data]
