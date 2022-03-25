import numpy as np
from mathutils import Euler

from . import abs_assignment
from ..cgt_blender.utils import objects
from ..cgt_naming import FACE, COLLECTIONS
from ..cgt_utils import m_V


class BridgeFace(abs_assignment.DataAssignment):
    def __init__(self):
        self.face = []

        self._mouth_driver = abs_assignment.CustomData()
        self._mouth_corner_driver = abs_assignment.CustomData()
        self.pivot, self.chin_driver = abs_assignment.CustomData(), abs_assignment.CustomData()
        self.eye_driver_L, self.eye_driver_R = abs_assignment.CustomData(), abs_assignment.CustomData()
        self.eyebrow_L, self.eyebrow_R = abs_assignment.CustomData(), abs_assignment.CustomData()

        self.rotation_data, self.driver_scale_data = None, None

        self.col_name = COLLECTIONS.face

    def init_references(self):
        references = {}
        for i in range(468):
            references[f'{i}'] = f"{FACE.face}{i}"
        self.face = objects.add_empties(references, 0.005)
        objects.add_list_to_collection(self.col_name, self.face, self.driver_col)

        mapping_driver = [FACE.right_eye_t, FACE.right_eye_b,
                          FACE.left_eye_t, FACE.left_eye_b,
                          FACE.mouth_t, FACE.mouth_b,
                          FACE.mouth_r, FACE.mouth_l,

                          FACE.eyebrow_in_l, FACE.eyebrow_mid_l,
                          FACE.eyebrow_out_l,
                          FACE.eyebrow_in_r, FACE.eyebrow_mid_r,
                          FACE.eyebrow_out_r
                          ]

        [self.init_bpy_driver_obj(
            abs_assignment.CustomData(), self.face, 0.01, name, self.col_name, "SPHERE", [0, 0, 0])
            for name in mapping_driver]

        drivers_array = [
            [self.pivot, 0.025, FACE.head, "SPHERE", [0, 0, 0]],
            [self._mouth_driver, 0.025, FACE.mouth, "CIRCLE", [0, -.1, -.1]],
            [self._mouth_corner_driver, 0.025, FACE.mouth_corners, "CIRCLE", [0, -.1, -.1]],
            [self.eye_driver_L, .01, FACE.left_eye, "CIRCLE", [-.05, -.05, .075]],
            [self.eye_driver_R, .01, FACE.right_eye, "CIRCLE", [.05, .05, .075]],
            [self.chin_driver, .01, FACE.chin, "SPHERE", [.0, -.05, -.25]],
            [self.eyebrow_L, .01, FACE.left_eyebrow, "CUBE", [.05, 0, .1]],
            [self.eyebrow_R, .01, FACE.right_eyebrow, "CUBE", [-.05, 0, .1]]
        ]
        # init driver objects
        [self.init_bpy_driver_obj(e[0], self.face, e[1], e[2], self.col_name, e[3], e[4]) for e in drivers_array]

        # set source position
        data = [[e[0].idx, e[4]] for e in drivers_array]
        self.translate(self.face, data, 0)

    def init_data(self):
        self.data = self.data[0]  # unnecessary nesting in raw data
        self.custom_landmark_origin()  # set face mesh to custom origin

        self.set_scale_driver_data()
        self.set_rotation_driver_data()

    def update(self):
        if self.has_duplicated_results(self.data):
            return

        self.euler_rotate(self.face, self.rotation_data, self.frame)
        self.scale(self.face, self.driver_scale_data, self.frame)
        self.set_position()

    def set_position(self):
        """Keyframes the position of input data."""
        try:
            self.translate(self.face, self.data, self.frame)
        except IndexError:
            print("VALUE ERROR WHILE ASSIGNING FACE POSITION")

    # region length between objects as scale to drivers
    def set_scale_driver_data(self):
        """ prepares mouth and eye driver data. """
        # setting up drivers
        avg_scale = m_V.vector_length(m_V.to_vector(self.data[362][1], self.data[263][1]))  # eye dist as avg scale
        # avg_scale = m_V.vector_length_2d(self.data[362][1], self.data[263][1], 'Z')  # eye dist as avg scale
        self.mouth_driver(avg_scale)
        self.eye_driver(avg_scale)
        self.eyebrow_drivers(avg_scale)

        # prep data
        self.driver_scale_data = [
            [self._mouth_corner_driver.idx, self._mouth_corner_driver.sca],
            [self._mouth_driver.idx, self._mouth_driver.sca],
            [self.eye_driver_L.idx, self.eye_driver_L.sca],
            [self.eye_driver_R.idx, self.eye_driver_R.sca],
            [self.eyebrow_L.idx, self.eyebrow_L.sca],
            [self.eyebrow_R.idx, self.eyebrow_R.sca]
        ]

    def mouth_driver(self, avg_scale):
        """ get mouth driver scale data. """
        # mouth width and height
        mouth_w = self.average_length_at_scale(62, 292, avg_scale)
        mouth_h = self.average_length_at_scale(13, 14, avg_scale)
        self.mouth_corners(avg_scale)
        self._mouth_driver.sca = [mouth_w, 0.001, mouth_h]

    def mouth_corners(self, avg_scale):
        corner_center = m_V.center_point(self.data[61][1], self.data[291][1])
        projected_center = m_V.project_point_on_vector(corner_center, self.data[0][1], self.data[17][1])
        mouth_height_center = m_V.center_point(self.data[0][1], self.data[17][1])

        left_vec = m_V.to_vector(projected_center, self.data[61][1])
        left_hv = m_V.to_vector(mouth_height_center, self.data[61][1])
        right_vec = m_V.to_vector(projected_center, self.data[291][1])
        right_hv = m_V.to_vector(mouth_height_center, self.data[291][1])

        right_corner_angle = m_V.angle_between(left_vec, left_hv)
        left_corner_angle = m_V.angle_between(right_vec, right_hv)

        # mouth corners (smile)
        # left_corner = self.average_length_at_scale(61, 92, avg_scale)
        # right_corner = self.average_length_at_scale(291, 322, avg_scale)

        self._mouth_corner_driver.sca = [left_corner_angle, 0.001, right_corner_angle]

    def eye_driver(self, avg_scale):
        """ get eye driver scale data. """
        eye_l = self.average_length_at_scale(386, 374, avg_scale)  # left eye
        eye_r = self.average_length_at_scale(159, 145, avg_scale)  # right eye

        self.eye_driver_L.sca = [1.5, 0.001, eye_l]
        self.eye_driver_R.sca = [1.5, 0.001, eye_r]

    def eyebrow_drivers(self, avg_scale):
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
        self.face_mesh_rotation()
        self.chin_rotation()

        head_rotation = self.quart_to_euler_combat(self.pivot.rot, self.pivot.idx, axis='XZY')
        chin_rotation = self.chin_driver.rot

        self.rotation_data = [
            [self.pivot.idx, head_rotation],
            [self.chin_driver.idx, chin_rotation]
        ]

    def chin_rotation(self):
        nose_dir = m_V.to_vector(self.data[168][1], self.data[2][1])
        chin_dir = m_V.to_vector(self.data[168][1], self.data[200][1])
        nose_dir_z, chin_dir_z = m_V.null_axis([nose_dir, chin_dir], 'X')
        nose_dir_x, chin_dir_x = m_V.null_axis([nose_dir, chin_dir], 'Z')

        z_angle = m_V.angle_between(nose_dir_z, chin_dir_z) * 1.8

        chin_rotation = m_V.rotate_towards(self.data[152][1], self.data[6][1], 'Y', 'Z')
        # due to the base angle it's required to offset the rotation
        self.chin_driver.rot = Euler(((z_angle - 3.14159 * .07) * 1.175, 0, 0))

    def face_mesh_rotation(self):
        """ calculate face quaternion using
        points to approximate the transformation matrix. """
        origin = np.array([0, 0, 0])
        # TODO: fix rotation (flip z & y)

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
        """ get length of 2d vector and normalize by 1d scale """
        length = m_V.vector_length(m_V.to_vector(self.data[p1][1], self.data[p2][1]))
        # length = m_V.vector_length_2d(self.data[p1][1], self.data[p2][1], 'Z')
        return m_V.vector_length(length / scale)

    def custom_landmark_origin(self):
        """ setting face mesh position to approximate origin """
        self.data = [[idx, [-lmrk[0], lmrk[2], -lmrk[1]]] for idx, lmrk in self.data[:468]]
        self.approximate_pivot_location()
        self.data = [[idx, np.array(lmrk) - np.array(self.pivot.loc)] for idx, lmrk in self.data[:468]]

    def approximate_pivot_location(self):
        """ approximate origin based on canonical face mesh geometry """
        right = m_V.center_point(np.array(self.data[447][1]), np.array(self.data[366][1]))  # temple.R
        left = m_V.center_point(np.array(self.data[137][1]), np.array(self.data[227][1]))  # temple.L
        self.pivot.loc = m_V.center_point(right, left)  # approximate origin
    # endregion
