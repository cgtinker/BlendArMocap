import importlib

import numpy as np
from mathutils import Vector

from blender import objects
from bridge.receiver import abstract_receiver
from utils import log
from utils.calc import m_P, m_V, m_M

importlib.reload(m_M)
importlib.reload(m_P)
importlib.reload(m_V)
importlib.reload(abstract_receiver)


class CustomData:
    idx = None
    loc = None
    rot = None
    sca = None
    obj = None


class BridgeFace(abstract_receiver.DataAssignment):
    def __init__(self, mode='realtime'):
        self.face = []
        self.pinned_rotation = None
        self.first_time = True

        # Drivers
        self.pivot = CustomData()
        self.mouth_driver = CustomData()
        self.eye_driver_L = CustomData()
        self.eye_driver_R = CustomData()

        self.col_name = "Face"
        self.init_references()

    def init_references(self):
        """Generate empty objects for debugging.
        references = {}
        for i in range(468):
            references[f'{i}'] = f"face_empty_{i}"

        # empty reference mesh
        self.face = objects.add_empties(references, 0.005)
        objects.add_list_to_collection(self.col_name, self.face)
        """
        # init face drivers
        pivot = self.init_driver_obj(self.pivot, 0.025, "face_rotation", "SPHERE", [0, 0, 0])
        mouth = self.init_driver_obj(self.mouth_driver, 0.025, "mouth_driver", "CIRCLE", [0, -.1, -.1])
        l_eye = self.init_driver_obj(self.eye_driver_L, 0.01, "left_eye_driver", "CIRCLE", [-.05, -.05, .075])
        r_eye = self.init_driver_obj(self.eye_driver_R, 0.01, "right_eye_driver", "CIRCLE", [.05, -.05, .075])

        # set driver start position
        drivers = [self.pivot, self.mouth_driver, self.eye_driver_R, self.eye_driver_L]
        data = [[driver.idx, driver.loc] for driver in drivers]
        self.translate(self.face, data, 0)

        # parent drivers
        objects.set_parents(pivot, [mouth, l_eye, r_eye])

    def init_driver_obj(self,
                        driver: CustomData,
                        size: float = 0.005,
                        name: str = "",
                        style: str = "CUBE",
                        position: [] = [0.0, 0.0, 0.0]):
        driver.obj = objects.add_empty(size, name, style)
        driver.loc = position
        self.face.append(driver.obj)
        driver.idx = len(self.face) - 1
        objects.add_obj_to_collection("Face_Drivers", driver.obj)
        return driver.obj

    def set_position(self, frame):
        self.set_custom_data(frame)
        """Keyframes the position of input data.
        try:
            self.translate(self.face, self.data, frame)
        except IndexError:
            log.logger.error("VALUE ERROR WHILE ASSIGNING FACE POSITION")
        """
    def set_custom_rotation(self, frame):
        self.face_mesh_rotation()
        euler = self.quart_to_euler_combat(self.pivot.rot, self.pivot.idx)
        custom_data = [[self.pivot.idx, euler]]
        self.euler_rotate(self.face, custom_data, frame)

    def set_custom_data(self, frame):
        self.data = self.data[0]        # unnecessary nesting in raw data
        self.custom_landmark_origin()   # set face mesh to custom origin

        # setting up drivers
        avg_scale = m_V.vector_length_2d(self.data[362][1], self.data[263][1], 'Z')     # eye dist as avg scale
        self.set_mouth_driver(avg_scale)
        self.set_eye_driver(avg_scale)

        # prep data
        data = [
            [self.mouth_driver.idx, self.mouth_driver.sca],
            [self.eye_driver_L.idx, self.eye_driver_L.sca],
            [self.eye_driver_R.idx, self.eye_driver_R.sca]
        ]

        # keyframe scale
        self.scale(self.face, data, frame)

    def set_mouth_driver(self, avg_scale):
        mouth_w = self.average_length_at_scale(62, 292, avg_scale)   # mouth width
        mouth_h = self.average_length_at_scale(13, 14, avg_scale)   # mouth height
        self.mouth_driver.sca = [mouth_w, 0.001, mouth_h]

    def set_eye_driver(self, avg_scale):
        eye_l = self.average_length_at_scale(386, 374, avg_scale)   # left eye
        eye_r = self.average_length_at_scale(159, 145, avg_scale)   # right eye

        self.eye_driver_L.sca = [1.5, 0.001, eye_l]
        self.eye_driver_R.sca = [1.5, 0.001, eye_r]

    def face_mesh_rotation(self):
        """ calculate face quaternion using
        points to approximate the transformation matrix. """
        origin = np.array([0, 0, 0])

        # approximate perpendicular points to origin
        forward_point = m_P.center_point(np.array(self.data[1][1]), np.array(self.data[4][1]))    # nose
        right_point = m_P.center_point(np.array(self.data[447][1]), np.array(self.data[366][1]))  # temple.R
        down_point = np.array(self.data[152][1])                                                  # chin

        # direction vectors from imaginary origin
        normal = m_V.normalize(m_V.to_vector(origin, forward_point))
        tangent = m_V.normalize(m_V.to_vector(origin, right_point))
        binormal = m_V.normalize(m_V.to_vector(origin, down_point))

        # generate matrix to decompose it and access quaternion rotation
        matrix = m_M.generate_matrix(tangent, normal, binormal)
        loc, quart, scale = m_M.decompose_matrix(matrix)
        self.pivot.rot = quart

    def average_length_at_scale(self, p1, p2, scale):
        """ get length of 2d vector and normalize by 1d scale """
        length = m_V.vector_length_2d(self.data[p1][1], self.data[p2][1], 'Z')
        return m_V.vector_length(length / scale)

    def custom_landmark_origin(self):
        """ setting face mesh to approximate origin """
        self.data = [[idx, [-lmrk[0], lmrk[2], -lmrk[1]]] for idx, lmrk in self.data[:468]]
        self.approximate_pivot_location()
        self.data = [[idx, np.array(lmrk) - np.array(self.pivot.loc)] for idx, lmrk in self.data[:468]]

    def approximate_pivot_location(self):
        """ approximate origin based on canonical face mesh geometry """
        right = m_P.center_point(np.array(self.data[447][1]), np.array(self.data[366][1]))  # temple.R
        left = m_P.center_point(np.array(self.data[137][1]), np.array(self.data[227][1]))   # temple.L
        self.pivot.loc = m_P.center_point(right, left)                                      # approximate origin

    def get_vector_by_entry(self, index):
        return Vector((self.data[0][index][1][0], self.data[0][index][1][1], self.data[0][index][1][2]))

    def allocate_memory(self, idx, data):
        """Store Detection data in memory."""
        self.memory_stack[f'{idx}'] = data[0]
