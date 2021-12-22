import importlib
from mathutils import Vector
from blender import objects
from bridge.receiver.abstract_receiver import DataAssignment
from utils import log, vector_math

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

        null = objects.add_empty(0.0005, "local_space")
        objects.set_parents(null, self.face[:len(self.face)])
        objects.add_list_to_collection(self.col_name, self.face)

    def set_position(self, frame):
        self.set_custom_data()
        """Keyframes the position of input data."""
        try:
            self.translate(self.face, self.data[0], frame)
        except IndexError:
            log.logger.error("VALUE ERROR WHILE ASSIGNING FACE POSITION")

    def set_custom_rotation(self, frame):
        pass

    def set_custom_data(self):
        """ Creates custom center data of the face. """
        cent = self.get_custom_center()
        self.data[0].append([468, [-cent[0], -cent[1], -cent[2]]])

    def get_custom_center(self):
        center = vector_math.get_center_point(self.get_vector_by_entry(234), self.get_vector_by_entry(454))
        return center

    def allocate_memory(self, idx, data):
        """Store Detection data in memory."""
        self.memory_stack[f'{idx}'] = data[0]

    def get_vector_by_entry(self, index):
        return Vector((self.data[0][index][1][0], self.data[0][index][1][1], self.data[0][index][1][2]))
