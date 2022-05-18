import numpy as np
from mathutils import Euler

from . import abs_assignment
from ..cgt_utils import m_V
from ..cgt_bridge import bpy_face_bridge


class BridgeFace(abs_assignment.DataProcessor):
    # used to assign custom data
    _mouth_driver = None
    _mouth_corner_driver = None
    pivot = None
    chin_driver = None
    eye_driver_L = None
    eye_driver_R = None
    eyebrow_L = None
    eyebrow_R = None

    # processed results
    rotation_data, driver_scale_data = None, None

    def __init__(self, bridge=bpy_face_bridge.BpyFaceReferences):
        # bridge to blender engine
        self.bridge = bridge

    def init_references(self):
        """ Generates objects for mapping. """
        self.bridge = self.bridge()
        _face, custom_data_arr = self.bridge.get_instances()

        # split only for readability
        self._mouth_driver, self._mouth_corner_driver, self.pivot, self.chin_driver, = custom_data_arr[:-4]
        self.eye_driver_L, self.eye_driver_R, self.eyebrow_L, self.eyebrow_R = custom_data_arr[4:]

    def init_data(self):
        """ Process the landmark detection results. """
        # remove nesting and set landmarks to custom origin
        self.data = self.data[0]
        self.custom_landmark_origin()

        # get distances and rotations to determine movements
        self.set_scale_driver_data()
        self.set_rotation_driver_data()

    def update(self):
        """ Assign the data processed data to references. """
        if self.has_duplicated_results(self.data):
            return

        self.bridge.set_position(self.data, self.frame)
        self.bridge.set_rotation(self.rotation_data, self.frame)
        self.bridge.set_scale(self.driver_scale_data, self.frame)

    def set_scale_driver_data(self):
        """ Prepares mouth and eye driver data. """
        # adds length between objects as scale to drivers using eye dist as avg scale
        avg_scale = m_V.vector_length(m_V.to_vector(self.data[362][1], self.data[263][1]))
        # get distances
        self.mouth_driver(avg_scale)
        self.eye_driver(avg_scale)
        self.eyebrow_drivers(avg_scale)

        # store prepared data
        self.driver_scale_data = [
            [self._mouth_corner_driver.idx, self._mouth_corner_driver.sca],
            [self._mouth_driver.idx, self._mouth_driver.sca],
            [self.eye_driver_L.idx, self.eye_driver_L.sca],
            [self.eye_driver_R.idx, self.eye_driver_R.sca],
            [self.eyebrow_L.idx, self.eyebrow_L.sca],
            [self.eyebrow_R.idx, self.eyebrow_R.sca]
        ]

    def mouth_driver(self, avg_scale):
        """ Get mouth driver scale data. """
        # mouth width and height
        mouth_w = self.average_length_at_scale(62, 292, avg_scale)  # mouth span
        mouth_h = self.average_length_at_scale(13, 14, avg_scale)  # mouth width
        self.mouth_corners(avg_scale)
        self._mouth_driver.sca = [mouth_w, 0.001, mouth_h]

    def mouth_corners(self, avg_scale):
        """ Calculates the angle from the mouth center to the mouth corner """
        # center point of mouth corners gets projected on vector from upper to lower lip
        corner_center = m_V.center_point(self.data[61][1], self.data[291][1])
        projected_center = m_V.project_point_on_vector(corner_center, self.data[0][1], self.data[17][1])
        # center point between upper and lower lip
        mouth_height_center = m_V.center_point(self.data[0][1], self.data[17][1])

        # vectors from center points to mouth corners
        left_vec = m_V.to_vector(projected_center, self.data[61][1])
        left_hv = m_V.to_vector(mouth_height_center, self.data[61][1])
        right_vec = m_V.to_vector(projected_center, self.data[291][1])
        right_hv = m_V.to_vector(mouth_height_center, self.data[291][1])

        # angle between the vectors expecting users don't record upside down
        if mouth_height_center[2] > projected_center[2]:
            right_corner_angle = m_V.angle_between(left_vec, left_hv)
            left_corner_angle = m_V.angle_between(right_vec, right_hv)
        else:
            right_corner_angle = -m_V.angle_between(left_vec, left_hv)
            left_corner_angle = -m_V.angle_between(right_vec, right_hv)

        self._mouth_corner_driver.sca = [left_corner_angle, 0.001, right_corner_angle]
        self._mouth_corner_driver.rot = [left_corner_angle, 0.001, right_corner_angle]

    def eye_driver(self, avg_scale):
        """ Get eye lid data. """
        # to determine if the eyes are opened or closed
        eye_l = self.average_length_at_scale(386, 374, avg_scale)  # left eye
        eye_r = self.average_length_at_scale(159, 145, avg_scale)  # right eye

        self.eye_driver_L.sca = [1.5, 0.001, eye_l]
        self.eye_driver_R.sca = [1.5, 0.001, eye_r]

    def eyebrow_drivers(self, avg_scale):
        """ Get the eyebrow data. """
        # to determine if the eyebrows are raised up or down
        eyebrow_in_l = self.average_length_at_scale(336, 338, avg_scale)
        eyebrow_mid_l = self.average_length_at_scale(296, 297, avg_scale)
        eyebrow_out_l = self.average_length_at_scale(334, 332, avg_scale)

        eyebrow_in_r = self.average_length_at_scale(107, 109, avg_scale)
        eyebrow_mid_r = self.average_length_at_scale(66, 67, avg_scale)
        eyebrow_out_r = self.average_length_at_scale(105, 103, avg_scale)

        self.eyebrow_L.sca = [eyebrow_in_l, eyebrow_mid_l, eyebrow_out_l]
        self.eyebrow_R.sca = [eyebrow_in_r, eyebrow_mid_r, eyebrow_out_r]

    # endregion

    def set_rotation_driver_data(self):
        """ Get face and chin rotation """
        self.face_mesh_rotation()
        self.chin_rotation()

        # check previous rotation to avoid discontinuity
        head_rotation = self.quart_to_euler_combat(self.pivot.rot, self.pivot.idx, axis='XZY')
        chin_rotation = self.chin_driver.rot

        # store rotation data
        self.rotation_data = [
            [self.pivot.idx, head_rotation],
            [self.chin_driver.idx, chin_rotation],
            [self._mouth_corner_driver.idx, self._mouth_corner_driver.rot]
        ]

    def chin_rotation(self):
        """ Calculate the chin rotation. """
        # draw vector from point between eyes to mouth and chin
        nose_dir = m_V.to_vector(self.data[168][1], self.data[2][1])
        chin_dir = m_V.to_vector(self.data[168][1], self.data[200][1])

        # calculate the X rotation
        nose_dir_z, chin_dir_z = m_V.null_axis([nose_dir, chin_dir], 'X')
        z_angle = m_V.angle_between(nose_dir_z, chin_dir_z) * 1.8

        # there is no x-rotation available in the detection result
        # nose_dir_x, chin_dir_x = m_V.null_axis([nose_dir, chin_dir], 'Z')
        # chin_rotation = m_V.rotate_towards(self.data[152][1], self.data[6][1], 'Y', 'Z')

        # due to the base angle it's required to offset the rotation
        self.chin_driver.rot = Euler(((z_angle - 3.14159 * .07) * 1.175, 0, 0))

    def face_mesh_rotation(self):
        """ Calculate face quaternion using
            points to approximate the transformation matrix. """
        origin = np.array([0, 0, 0])

        forward_point = m_V.center_point(np.array(self.data[1][1]), np.array(self.data[4][1]))  # nose
        right_point = m_V.center_point(np.array(self.data[447][1]), np.array(self.data[366][1]))  # temple.R
        down_point = np.array(self.data[152][1])  # chin

        # direction vectors from imaginary origin
        normal = m_V.normalize(m_V.to_vector(origin, forward_point))
        tangent = m_V.normalize(m_V.to_vector(origin, right_point))
        binormal = m_V.normalize(m_V.to_vector(origin, down_point))

        # generate matrix to decompose it and access quaternion rotation
        matrix = m_V.generate_matrix(tangent, normal, binormal)
        loc, quart, scale = m_V.decompose_matrix(matrix)

        self.pivot.rot = quart

    # region cgt_utils
    def average_length_at_scale(self, p1, p2, scale):
        """ Get length of 2d vector and normalize by 1d scale """
        length = m_V.vector_length(m_V.to_vector(self.data[p1][1], self.data[p2][1]))
        return m_V.vector_length(length / scale)

    def custom_landmark_origin(self):
        """ Sets face mesh position to approximate origin """
        self.data = [[idx, [-lmrk[0], lmrk[2], -lmrk[1]]] for idx, lmrk in self.data[:468]]
        self.approximate_pivot_location()
        self.data = [[idx, np.array(lmrk) - np.array(self.pivot.loc)] for idx, lmrk in self.data[:468]]

    def approximate_pivot_location(self):
        """ Sets to approximate origin based on canonical face mesh geometry """
        right = m_V.center_point(np.array(self.data[447][1]), np.array(self.data[366][1]))  # temple.R
        left = m_V.center_point(np.array(self.data[137][1]), np.array(self.data[227][1]))  # temple.L
        self.pivot.loc = m_V.center_point(right, left)  # approximate origin
    # endregion
