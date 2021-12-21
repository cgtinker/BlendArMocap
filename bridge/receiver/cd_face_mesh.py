import importlib
from mathutils import Vector
from blender import objects
from bridge.receiver.abstract_receiver import DataAssignment
from utils import log, vector_math
import numpy as np

importlib.reload(vector_math)


class BridgeFace(DataAssignment):
    def __init__(self, mode='realtime'):
        self.references = {
        }
        self.face = None
        self.col_name = "Face"
        self.init_references()

    def init_references(self):
        """Generate empty objects."""
        for i in range(468):
            self.references[f'{i}'] = f"face_empty_{i}"
        self.face = objects.add_empties(self.references, 0.005)

        # empties to create local space data
        vert_orientation = objects.add_empty(0.05, "vert_orientation", "PLAIN_AXES")
        hor_orientation = objects.add_empty(0.05, "hor_orientation", "PLAIN_AXES")

        null = objects.add_empty(0.0005, "local_space")
        origin = objects.add_empty(0.005, "face_parent")

        # parenting empties for further manipulation
        objects.set_parents(null, self.face[:len(self.face)])
        self.face.append(null)  # 469
        self.face.append(hor_orientation)  # 470
        self.face.append(vert_orientation)  # 471

        objects.set_parent(origin, null)
        objects.set_parent(origin, hor_orientation)
        objects.set_parent(origin, vert_orientation)

        self.face.append(origin)  # 472

        # adding drivers to col
        objects.add_list_to_collection(self.col_name, self.face)

    def set_position(self, frame):
        self.set_custom_data()
        """Keyframes the position of input data."""
        try:
            self.translate(self.face, self.data[0], frame)
        except IndexError:
            log.logger.error("VALUE ERROR WHILE ASSIGNING FACE POSITION")

    def set_custom_rotation(self, frame):
        """ Custom rotation data null global data. """
        v = vector_math
        center = self.get_custom_center()

        hor = v.rotate_towards(
            center,
            self.prep_vector(self.get_vector_by_entry(398)),
            track='X',
            up='Z'
        )
        hor = self.quart_to_euler_combat(hor, 0)

        vert = v.rotate_towards(
            center,
            self.prep_vector(self.get_vector_by_entry(173)),
            track='X',
            up='Z'
        )
        vert = self.quart_to_euler_combat(vert, 1)
        print(hor, "\n", center,"\n", self.get_vector_by_entry(398),"\n","\n")

        r_data = [
            [469, [hor[0], hor[1], hor[2]]],
            [470, [vert[0], vert[1], vert[2]]]
            # [470, [(vert[0] + hor[0]) / 2, (vert[1] + hor[0]) / 2, (vert[2] + hor[0]) / 2]]
        ]

        # keyframe res
        self.euler_rotate(self.face, r_data, frame)

    def old_custom_rotation(self, frame):
        v = vector_math
        # vector facing X axis
        hor = v.rotate_towards(
            self.prep_vector(self.get_vector_by_entry(123)),
            self.prep_vector(self.get_vector_by_entry(345)),
            track='Z',
            up='Y'
        )
        hor = self.quart_to_euler_combat(hor, 0)

        # vector facing Z axis
        vert = v.rotate_towards(
            self.prep_vector(self.get_vector_by_entry(152)),
            self.prep_vector(self.get_vector_by_entry(10)),
            track='Z',
            up='X'
        )
        vert = self.quart_to_euler_combat(vert, 1)

        # setup data format
        r_data = [
            [469, [hor[0], hor[1], hor[2]]],
            # [470, [vert[0], vert[1], vert[2]]]
            [470, [(vert[0] + hor[0]) / 2, (vert[1] + hor[0]) / 2, (vert[2] + hor[0]) / 2]]
        ]

        # keyframe res
        self.euler_rotate(self.face, r_data, frame)

    def set_custom_data(self):
        """ Creates custom center data of the face. """
        cent = self.get_custom_center()
        # center = vector_math.get_center_point(self.get_vector_by_entry(234), self.get_vector_by_entry(454))
        # self.data[0].append([468, [-center[0], -center[1], -center[2]]])
        self.data[0].append([468, [-cent[0], -cent[1], -cent[2]]])

    def get_custom_center(self):
        center = vector_math.get_center_point(self.get_vector_by_entry(234), self.get_vector_by_entry(454))
        return center
        #hoz = vector_math.get_center_point(self.get_vector_by_entry(33), self.get_vector_by_entry(416))
        #up = vector_math.get_center_point(self.get_vector_by_entry(192), self.get_vector_by_entry(263))
        #return vector_math.get_center_point(up, hoz)

    def allocate_memory(self, idx, data):
        """Store Detection data in memory."""
        self.memory_stack[f'{idx}'] = data[0]

    def get_vector_by_entry(self, index):
        return Vector((self.data[0][index][1][0], self.data[0][index][1][1], self.data[0][index][1][2]))
        #return self.data[0][index][1]
