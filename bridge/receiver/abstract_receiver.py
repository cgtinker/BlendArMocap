from abc import ABC, abstractmethod
from utils.writer import json_writer
from mathutils import Vector, Euler
from utils import vector_math


class DataAssignment(ABC):
    data = None
    references = None
    prev_rotation = {}
    memory_stack = {}

    # region abstract methods
    @abstractmethod
    def init_references(self):
        """ Initialize Empties for further manipulation. """
        pass

    @abstractmethod
    def set_position(self, frame):
        """ Prepare data and set translation data. """
        pass

    @abstractmethod
    def set_custom_rotation(self, frame):
        """ Prepare and set custom euler rotation data. """
        pass
    # endregion

    # region bpy object oriented
    @staticmethod
    def translate(target, data, frame):
        """ Translates and keyframes bpy empty objects. """
        try:
            for p in data:
                target[p[0]].location = Vector((p[1]))
                target[p[0]].keyframe_insert(data_path="location", frame=frame)

        except IndexError:
            print("missing index!!!")
            pass

    @staticmethod
    def scale(target, data, frame):
        try:
            for p in data:
                print("SETTING SCALE:", p[0], p[1])
                target[p[0]].scale = Vector((p[1]))
                target[p[0]].keyframe_insert(data_path="scale", frame=frame)
        except IndexError:
            print("missing index!!!")
            pass

    @staticmethod
    def prep_vector(vec):
        return Vector((-vec[0], vec[2], -vec[1]))

    def euler_rotate(self, target, data, frame):
        """ Translates and keyframes bpy empty objects. """
        try:
            for p in data:
                target[p[0]].rotation_euler = p[1]
                target[p[0]].rotation_euler = Euler((p[1][0], p[1][1], p[1][2]), 'XYZ')
                target[p[0]].keyframe_insert(data_path="rotation_euler", frame=frame)
                self.prev_rotation[p[0]] = p[1]
        except IndexError:
            print("missing index!!!")
            pass

    def quart_to_euler_combat(self, quart, idx):
        """ Converts quart to euler rotation while comparing with previous rotation. """
        if len(self.prev_rotation) > 0:
            try:
                combat = self.prev_rotation[idx]
                return vector_math.to_euler(quart, combat, 'XYZ')
            except KeyError:
                print("invalid id to euler combat")
                return vector_math.to_euler(quart)
        else:
            return vector_math.to_euler(quart)

    @staticmethod
    def write_json(filename, data):
        """Writes a .json file for async processing"""
        writer = json_writer.JsonWriter(filename + '.json')
        writer.chunks = data
        writer.write()
    # endregion

    @staticmethod
    def add_objects_to_collection(objects, collection_name):
        pass

    @staticmethod
    def add_parent_to_object(objects, parent_name):
        pass

    def get_vector_by_entry(self, index):
        return Vector((self.data[index][1][0], self.data[index][1][1], self.data[index][1][2]))
