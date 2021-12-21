import importlib

import numpy as np
from mathutils import Vector

from blender import objects
from bridge.receiver import abstract_receiver
from utils import log, vector_math
from utils.calc import m_P, m_V, m_M

importlib.reload(vector_math)
importlib.reload(m_M)
importlib.reload(m_P)
importlib.reload(m_V)
importlib.reload(abstract_receiver)


class CustomData:
    idx = None
    rot = None
    loc = None
    obj = None


class BridgeFace(abstract_receiver.DataAssignment):
    def __init__(self, mode='realtime'):
        self.face = None
        self.pinned_rotation = None
        self.first_time = True
        self.pivot = CustomData()
        self.col_name = "Face"
        self.init_references()

    def init_references(self):
        """Generate empty objects."""
        references = {}
        for i in range(468):
            references[f'{i}'] = f"face_empty_{i}"

        # empty reference objects
        self.face = objects.add_empties(references, 0.005)
        objects.add_list_to_collection(self.col_name, self.face)

        # imaginary pivot
        self.pivot.obj = objects.add_empty(0.05, "face_pivot", "PLAIN_AXES")
        self.face.append(self.pivot.obj)  # 469
        self.pivot.idx = len(self.face)-1
        print(self.pivot.idx)
        objects.add_list_to_collection("Face_Drivers", [self.pivot.obj])

    def set_position(self, frame):
        self.set_custom_data()
        """Keyframes the position of input data."""
        try:
            self.translate(self.face, self.data, frame)
        except IndexError:
            log.logger.error("VALUE ERROR WHILE ASSIGNING FACE POSITION")

    def set_custom_rotation(self, frame):
        self.face_mesh_rotation()
        euler = self.quart_to_euler_combat(self.pivot.rot, self.pivot.idx)
        custom_data = [[self.pivot.idx, euler]]
        self.euler_rotate(self.face, custom_data, frame)

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

    def set_custom_data(self):
        self.data = self.data[0]        # unnecessary nesting in raw data
        self.custom_landmark_origin()   # set face mesh origin to custom origin

    def allocate_memory(self, idx, data):
        """Store Detection data in memory."""
        self.memory_stack[f'{idx}'] = data[0]

    def get_vector_by_entry(self, index):
        return Vector((self.data[0][index][1][0], self.data[0][index][1][1], self.data[0][index][1][2]))

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