import importlib

import numpy as np

import utils.m_V
from blender import objects
from bridge import abs_assignment
from utils import m_V

importlib.reload(m_V)
importlib.reload(abs_assignment)


class BridgeFace(abs_assignment.DataAssignment):
    def __init__(self):
        self.face = []
        self.pinned_rotation = None
        self.first_time = True

        # Drivers
        self.pivot = abs_assignment.CustomData()
        self._mouth_driver = abs_assignment.CustomData()
        self.eye_driver_L = abs_assignment.CustomData()
        self.eye_driver_R = abs_assignment.CustomData()

        self.rotation_data, self.driver_scale_data = None, None

        self.col_name = "cgt_face"

    def init_references(self):
        references = {}
        for i in range(468):
            references[f'{i}'] = f"cgt_face_empty_{i}"
        self.face = objects.add_empties(references, 0.005)
        objects.add_list_to_collection(self.col_name, self.face, self.driver_col)

        # init face drivers
        pivot = self.init_bpy_driver_obj(
            self.pivot, self.face, 0.025, "face_rotation", self.col_name, "SPHERE", [0, 0, 0])
        mouth = self.init_bpy_driver_obj(
            self._mouth_driver, self.face, 0.025, "mouth_driver", self.col_name, "CIRCLE", [0, -.1, -.1])
        l_eye = self.init_bpy_driver_obj(
            self.eye_driver_L, self.face, 0.01, "left_eye_driver", self.col_name, "CIRCLE", [-.05, -.05, .075])
        r_eye = self.init_bpy_driver_obj(
            self.eye_driver_R, self.face, 0.01, "right_eye_driver", self.col_name, "CIRCLE", [.05, -.05, .075])

        # set driver start position
        drivers = [self.pivot, self._mouth_driver, self.eye_driver_R, self.eye_driver_L]
        data = [[driver.idx, driver.loc] for driver in drivers]
        self.translate(self.face, data, 0)

        # parent drivers
        objects.set_parents(pivot, [mouth, l_eye, r_eye])

    def init_data(self):
        self.data = self.data[0]  # unnecessary nesting in raw data
        self.custom_landmark_origin()  # set face mesh to custom origin

        self.set_scale_driver_data()
        self.face_mesh_rotation()

    def update(self):
        euler = self.quart_to_euler_combat(self.pivot.rot, self.pivot.idx)
        self.rotation_data = [[self.pivot.idx, euler]]
        self.euler_rotate(self.face, self.rotation_data, self.frame)
        self.scale(self.face, self.driver_scale_data, self.frame)
        self.set_position()

    def set_position(self):
        """Keyframes the position of input data."""
        try:
            self.translate(self.face, self.data, self.frame)
        except IndexError:
            print("VALUE ERROR WHILE ASSIGNING FACE POSITION")

    def set_scale_driver_data(self):
        """ prepares mouth and eye driver data. """
        # setting up drivers
        avg_scale = m_V.vector_length_2d(self.data[362][1], self.data[263][1], 'Z')  # eye dist as avg scale
        self.mouth_driver(avg_scale)
        self.eye_driver(avg_scale)

        # prep data
        self.driver_scale_data = [
            [self._mouth_driver.idx, self._mouth_driver.sca],
            [self.eye_driver_L.idx, self.eye_driver_L.sca],
            [self.eye_driver_R.idx, self.eye_driver_R.sca]
        ]

    def mouth_driver(self, avg_scale):
        """ get mouth driver scale data. """
        mouth_w = self.average_length_at_scale(62, 292, avg_scale)  # mouth width
        mouth_h = self.average_length_at_scale(13, 14, avg_scale)  # mouth height
        self._mouth_driver.sca = [mouth_w, 0.001, mouth_h]

    def eye_driver(self, avg_scale):
        """ get eye driver scale data. """
        eye_l = self.average_length_at_scale(386, 374, avg_scale)  # left eye
        eye_r = self.average_length_at_scale(159, 145, avg_scale)  # right eye

        self.eye_driver_L.sca = [1.5, 0.001, eye_l]
        self.eye_driver_R.sca = [1.5, 0.001, eye_r]

    def face_mesh_rotation(self):
        """ calculate face quaternion using
        points to approximate the transformation matrix. """
        origin = np.array([0, 0, 0])

        # approximate perpendicular points to origin
        forward_point = utils.m_V.center_point(np.array(self.data[1][1]), np.array(self.data[4][1]))  # nose
        right_point = utils.m_V.center_point(np.array(self.data[447][1]), np.array(self.data[366][1]))  # temple.R
        down_point = np.array(self.data[152][1])  # chin

        # direction vectors from imaginary origin
        normal = m_V.normalize(m_V.to_vector(origin, forward_point))
        tangent = m_V.normalize(m_V.to_vector(origin, right_point))
        binormal = m_V.normalize(m_V.to_vector(origin, down_point))

        # generate matrix to decompose it and access quaternion rotation
        matrix = utils.m_V.generate_matrix(tangent, normal, binormal)
        loc, quart, scale = utils.m_V.decompose_matrix(matrix)
        self.pivot.rot = quart

    def average_length_at_scale(self, p1, p2, scale):
        """ get length of 2d vector and normalize by 1d scale """
        length = m_V.vector_length_2d(self.data[p1][1], self.data[p2][1], 'Z')
        return m_V.vector_length(length / scale)

    def custom_landmark_origin(self):
        """ setting face mesh position to approximate origin """
        self.data = [[idx, [-lmrk[0], lmrk[2], -lmrk[1]]] for idx, lmrk in self.data[:468]]
        self.approximate_pivot_location()
        self.data = [[idx, np.array(lmrk) - np.array(self.pivot.loc)] for idx, lmrk in self.data[:468]]

    def approximate_pivot_location(self):
        """ approximate origin based on canonical face mesh geometry """
        right = utils.m_V.center_point(np.array(self.data[447][1]), np.array(self.data[366][1]))  # temple.R
        left = utils.m_V.center_point(np.array(self.data[137][1]), np.array(self.data[227][1]))  # temple.L
        self.pivot.loc = utils.m_V.center_point(right, left)  # approximate origin
