import logging
import numpy as np
from mathutils import Euler

from .calc_utils import ProcessorUtils, CustomData
from . import cgt_math
from ..cgt_patterns import cgt_nodes


class FaceRotationCalculator(cgt_nodes.CalculatorNode, ProcessorUtils):
    # processed results
    def __init__(self):
        # increase shape to add specific driver data (maybe not required for the face)
        n = 468
        self.rotation_data = []
        custom_data_arr = [CustomData(idx+n) for idx in range(0, 5)]
        self.pivot, self.chin_driver, self.left_mouth_corner, self.right_mouth_corner, *_ = custom_data_arr

    def update(self, data, frame=-1):
        """ Process the landmark detection results. """
        """ Assign the data processed data to references. """
        # remove nesting and set landmarks to custom origin
        try:
            if len(data[0][0]) == 0:
                return [[], [], []], frame
        except IndexError:
            logging.error(f"Index Error occurred: {data}, {frame} - check face nodes")
            return [[], [], []], frame

        self.data = data[0]
        if len(self.data) < 468:
            return [[], [], []], frame

        # increase the data size to hold custom data (check __init__)
        for i in range(4):
            self.data.append([468+i, [0., 0., 0.]])
        self.custom_landmark_origin()

        # get distances and rotations to determine movements
        self.set_rotation_driver_data()
        if self.has_duplicated_results(self.data, "face"):
            return [[], [], []], frame
        return [self.data, self.rotation_data, []], frame

    def get_processed_data(self):
        """ Returns the processed data """
        return self.data, self.rotation_data, [], self.frame, self.has_duplicated_results(self.data)

    def mouth_corners(self):
        """ Calculates the angle from the mouth center to the mouth corner """
        # center point of mouth corners gets projected on vector from upper to lower lip
        corner_center = cgt_math.center_point(self.data[61][1], self.data[291][1])
        projected_center = cgt_math.project_point_on_vector(corner_center, self.data[0][1], self.data[17][1])
        # center point between upper and lower lip
        mouth_height_center = cgt_math.center_point(self.data[0][1], self.data[17][1])

        # vectors from center points to mouth corners
        left_vec = cgt_math.to_vector(projected_center, self.data[61][1])
        left_hv = cgt_math.to_vector(mouth_height_center, self.data[61][1])
        right_vec = cgt_math.to_vector(projected_center, self.data[291][1])
        right_hv = cgt_math.to_vector(mouth_height_center, self.data[291][1])

        # angle between the vectors expecting users don't record upside down
        if mouth_height_center[2] > projected_center[2]:
            right_corner_angle = cgt_math.angle_between(left_vec, left_hv)
            left_corner_angle = cgt_math.angle_between(right_vec, right_hv)
        else:
            right_corner_angle = -cgt_math.angle_between(left_vec, left_hv)
            left_corner_angle = -cgt_math.angle_between(right_vec, right_hv)

        self.left_mouth_corner.loc = [0, 0, left_corner_angle]
        self.right_mouth_corner.loc = [0, 0, right_corner_angle]
        self.data.append([self.left_mouth_corner.idx, self.left_mouth_corner.loc])
        self.data.append([self.right_mouth_corner.idx, self.right_mouth_corner.loc])

    def set_rotation_driver_data(self):
        """ Get face and chin rotation """
        self.face_mesh_rotation()
        try:
            head_rotation = self.try_get_euler(self.pivot.rot, prev_rot_idx=self.pivot.idx)
            # head_rotation = self.quart_to_euler_combat(self.pivot.rot, self.pivot.idx, axis='XZY')
        except AttributeError:
            logging.warning("Exchange method in cgt_maths for other targets than blender.")
            head_rotation = [0, 0, 0]

        self.chin_rotation()
        chin_rotation = self.chin_driver.rot
        # store rotation data
        self.rotation_data = [
            [self.pivot.idx, head_rotation],
            [self.chin_driver.idx, chin_rotation],
            # [self._mouth_corner_driver.idx, self._mouth_corner_driver.rot]
        ]

    def chin_rotation(self):
        """ Calculate the chin rotation. """
        # draw vector from point between eyes to mouth and chin
        nose_dir = cgt_math.to_vector(self.data[168][1], self.data[2][1])
        chin_dir = cgt_math.to_vector(self.data[168][1], self.data[200][1])

        # calculate the Z rotation
        nose_dir_z, chin_dir_z = cgt_math.null_axis([nose_dir, chin_dir], 'X')
        z_angle = cgt_math.angle_between(nose_dir_z, chin_dir_z) * 1.8

        # in the detection results is no X-rotation available
        # nose_dir_x, chin_dir_x = m_V.null_axis([nose_dir, chin_dir], 'Z')
        # chin_rotation = m_V.rotate_towards(self.data[152][1], self.data[6][1], 'Y', 'Z')

        # due to the base angle it's required to offset the rotation
        self.chin_driver.rot = Euler(((z_angle - 3.14159 * .07) * 1.175, 0, 0))

    def face_mesh_rotation(self):
        """ Calculate face quaternion using
            points to approximate the transformation matrix. """
        origin = np.array([0, 0, 0])

        forward_point = cgt_math.center_point(np.array(self.data[1][1]), np.array(self.data[4][1]))  # nose
        right_point = cgt_math.center_point(np.array(self.data[447][1]), np.array(self.data[366][1]))  # temple.R
        down_point = np.array(self.data[152][1])  # chin

        # direction vectors from imaginary origin
        normal = cgt_math.normalize(cgt_math.to_vector(origin, forward_point))
        tangent = cgt_math.normalize(cgt_math.to_vector(origin, right_point))
        binormal = cgt_math.normalize(cgt_math.to_vector(origin, down_point))

        # generate matrix to decompose it and access quaternion rotation
        try:
            matrix = cgt_math.generate_matrix(tangent, normal, binormal)
            loc, quart, scale = cgt_math.decompose_matrix(matrix)
        except TypeError:
            logging.warning("Exchange method in cgt_math for other targets than Blender.")
            quart = None
        self.pivot.rot = quart

    # region cgt_utils
    def custom_landmark_origin(self):
        """ Sets face mesh position to approximate origin """
        self.data = [[idx, np.array([-lmrk[0], lmrk[2], -lmrk[1]])] for idx, lmrk in self.data[:468]]
        self.approximate_pivot_location()
        self.data = [[idx, np.array(lmrk) - np.array(self.pivot.loc)] for idx, lmrk in self.data[:468]]

    def approximate_pivot_location(self):
        """ Sets to approximate origin based on canonical face mesh geometry """
        right = cgt_math.center_point(np.array(self.data[447][1]), np.array(self.data[366][1]))  # temple.R
        left = cgt_math.center_point(np.array(self.data[137][1]), np.array(self.data[227][1]))  # temple.L
        self.pivot.loc = cgt_math.center_point(right, left)  # approximate origin
    # endregion
