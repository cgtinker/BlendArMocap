'''
Copyright (C) cgtinker, cgtinker.com, hello@cgtinker.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

from abc import abstractmethod

from .custom_data_container import CustomData
from ..cgt_blender.utils import objects
from ..cgt_naming import COLLECTIONS
from mathutils import Vector
from . import bridge_interface


class BpyInstanceProvider(bridge_interface.BridgeInterface):
    parent_col = COLLECTIONS.drivers
    prev_rotation = {}

    @abstractmethod
    def get_instances(self):
        pass

    @abstractmethod
    def set_position(self, data, frame):
        pass

    @abstractmethod
    def set_rotation(self, data, frame):
        pass

    @abstractmethod
    def set_scale(self, data, frame):
        pass

    def init_bpy_driver_obj(
            self,
            driver: CustomData, ref_in_array: [],
            size: float = 0.005, name: str = "", col_name: str = COLLECTIONS.drivers,
            style: str = "CUBE", position: [] = None, is_parent: bool = False,
            children: [] = None):
        """ Creates a Custom Data object """
        # create object
        driver.obj = objects.add_empty(size, name, style)
        if position is None:
            position = [0, 0, 0]

        # parenting
        driver.loc = position
        if is_parent:
            if children is None:
                children = []
            objects.set_parents(driver.obj, children)

        # add to arr
        ref_in_array.append(driver.obj)
        driver.idx = len(ref_in_array) - 1

        # add to collection
        objects.add_obj_to_collection(col_name, driver.obj, self.parent_col)
        return driver.obj

    @staticmethod
    def translate(target, data, frame):
        """ Translates and keyframes bpy empty objects. """
        try:
            for p in data:
                target[p[0]].matrix_world.translation = Vector((p[1]))
                # target[p[0]].location = Vector((p[1]))
                target[p[0]].keyframe_insert(data_path="location", frame=frame)

        except IndexError:
            print(f"missing translation index at {frame}")
            pass

    @staticmethod
    def scale(target, data, frame):
        try:
            for p in data:
                target[p[0]].scale = Vector((p[1]))
                target[p[0]].keyframe_insert(data_path="scale", frame=frame)
        except IndexError:
            print(f"missing scale index at {data}, {frame}")
            pass

    @staticmethod
    def quaternion_rotate(target, data, frame):
        """ Translates and keyframes bpy empty objects. """
        try:
            for p in data:
                target[p[0]].rotation_quaternion = p[1]
                target[p[0]].keyframe_insert(data_path="rotation_quaternion", frame=frame)
        except IndexError:
            print(f"missing quat_euler_rotate index {data}, {frame}")
            pass

    def euler_rotate(self, target, data, frame, idx_offset=0):
        """ Translates and keyframes bpy empty objects. """
        try:
            for p in data:
                target[p[0]].rotation_euler = p[1]
                target[p[0]].keyframe_insert(data_path="rotation_euler", frame=frame)
                self.prev_rotation[p[0] + idx_offset] = p[1]
        except IndexError:
            print(f"missing euler_rotate index at {data}, {frame}")
            pass
