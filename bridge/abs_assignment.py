from abc import ABC, abstractmethod
import utils.m_V
from mathutils import Vector
from blender import objects


class CustomData:
    idx = None
    loc = None
    rot = None
    sca = None
    obj = None


class DataAssignment(ABC):
    data = None
    frame = 0
    references = None
    prev_rotation = {}
    memory_stack = {}
    driver_col = "cgt_drivers"

    # region abstract methods
    @abstractmethod
    def init_references(self):
        """ initialize reference objects for mapping. """
        pass

    @abstractmethod
    def init_data(self):
        """ setup data before assignment. """
        pass

    @abstractmethod
    def update(self):
        """ updates every mp solution received. """
        pass
    # endregion

    # region init helper
    def init_bpy_driver_obj(self,
                            driver: CustomData,
                            ref_in_array: [],
                            size: float = 0.005,
                            name: str = "",
                            col_name: str = "cgt_drivers",
                            style: str = "CUBE",
                            position: [] = [0.0, 0.0, 0.0],
                            is_parent: bool = False,
                            children: [] = []):

        driver.obj = objects.add_empty(size, name, style)
        driver.loc = position
        if is_parent:
            objects.set_parents(driver.obj, children)

        ref_in_array.append(driver.obj)
        driver.idx = len(ref_in_array) - 1
        objects.add_obj_to_collection(col_name, driver.obj, self.driver_col)
        return driver.obj
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
                target[p[0]].scale = Vector((p[1]))
                target[p[0]].keyframe_insert(data_path="scale", frame=frame)
        except IndexError:
            print("missing index!!!")
            pass

    @staticmethod
    def quaternion_rotate(target, data, frame):
        """ Translates and keyframes bpy empty objects. """
        try:
            for p in data:
                target[p[0]].rotation_quaternion = p[1]
                target[p[0]].keyframe_insert(data_path="rotation_quaternion", frame=frame)
        except IndexError:
            print("missing quat_euler_rotate index!!!")
            pass

    def euler_rotate(self, target, data, frame, idx_offset=0):
        """ Translates and keyframes bpy empty objects. """
        try:
            for p in data:
                target[p[0]].rotation_euler = p[1]
                target[p[0]].keyframe_insert(data_path="rotation_euler", frame=frame)
                self.prev_rotation[p[0]+idx_offset] = p[1]
        except IndexError:
            print("missing euler_rotate index!!!")
            pass

    def quart_to_euler_combat(self, quart, idx, idx_offset=0):
        """ Converts quart to euler rotation while comparing with previous rotation. """
        if len(self.prev_rotation) > 0:
            try:
                combat = self.prev_rotation[idx+idx_offset]
                return utils.m_V.to_euler(quart, combat, 'XYZ')
            except KeyError:
                print("invalid id to euler combat", idx, self.frame)
                return utils.m_V.to_euler(quart)
        else:
            return utils.m_V.to_euler(quart)
    # endregion
