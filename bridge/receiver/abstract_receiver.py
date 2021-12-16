from abc import ABC, abstractmethod
from utils.writer import json_writer
from mathutils import Vector, Euler


class DataAssignment(ABC):
    data = None
    references = None
    memory_stack = {}

    @abstractmethod
    def init_references(self):
        """ Initialize Empties for further manipulation. """
        pass

    @abstractmethod
    def set_position(self, frame):
        """ Prepare data for translation of empties. """
        pass

    @abstractmethod
    def set_custom_rotation(self, frame):
        """ Prepare data for setting euler rotation. """
        pass

    @staticmethod
    def write_json(filename, data):
        """Writes a .json file for async processing"""
        writer = json_writer.JsonWriter(filename+'.json')
        writer.chunks = data
        writer.write()

    @staticmethod
    def translate(target, data, frame):
        """ Translates and keyframes bpy empty objects. """
        try:
            for p in data:
                target[p[0]].location = Vector((-p[1][0], p[1][2], -p[1][1]))
                target[p[0]].keyframe_insert(data_path="location", frame=frame)

        except IndexError:
            print("missing index!!!")
            pass

    @staticmethod
    def euler_rotate(target, data, frame):
        """ Translates and keyframes bpy empty objects. """
        try:
            for p in data:
                target[p[0]].rotation_euler = Euler((p[1][0], p[1][1], p[1][2]), 'XYZ')
                target[p[0]].keyframe_insert(data_path="rotation_euler", frame=frame)

        except IndexError:
            print("missing index!!!")
            pass

    def get_vector_by_entry(self, index):
        return Vector((self.data[index][1][0], self.data[index][1][1], self.data[index][1][2]))

    @staticmethod
    def add_objects_to_collection(objects, collection_name):
        pass

    @staticmethod
    def add_parent_to_object(objects, parent_name):
        pass
