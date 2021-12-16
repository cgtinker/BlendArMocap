from blender import objects
from utils import log
from bridge.receiver.abstract_receiver import DataAssignment


class BridgeFace(DataAssignment):
    def __init__(self, mode='realtime'):
        self.references = {
        }
        self.face = None
        self.col_name = "Face"
        self.init_references()

    def init_references(self):
        """Generate empty objects."""
        for i in range(467):
            self.references[f'{i}'] = f"face_empty_{i}"
        self.face = objects.add_empties(self.references, 0.005)

        # generate custom object for nulling positions
        parent = objects.add_empty(0.025, "face_parent")
        objects.set_parents(parent, self.face)
        self.face.append(parent)

        objects.add_list_to_collection(self.col_name, self.face)

    def set_position(self, frame):
        """Keyframe the position of input data."""
        try:
            self.translate(self.face, self.data[0], frame)
        except IndexError:
            log.logger.error("VALUE ERROR WHILE ASSIGNING FACE POSITION")

    def set_custom_rotation(self, frame):
        pass

    def allocate_memory(self, idx, data):
        """Store Detection data in memory."""
        self.memory_stack[f'{idx}'] = data[0]