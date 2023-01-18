from __future__ import annotations
from typing import List
import logging
from abc import abstractmethod

import bpy.types

from ..cgt_naming import COLLECTIONS
from mathutils import Vector, Quaternion, Euler
from ..cgt_patterns import cgt_nodes


class BpyOutputNode(cgt_nodes.OutputNode):
    parent_col = COLLECTIONS.drivers
    prev_rotation = {}

    @abstractmethod
    def update(self, data, frame):
        pass

    @staticmethod
    def translate(target: List[bpy.types.Object], data, frame: int):
        """ Translates and keyframes bpy empty objects. """
        try:
            for landmark in data:
                target[landmark[0]].location = Vector((landmark[1]))
                target[landmark[0]].keyframe_insert(data_path="location", frame=frame)

        except IndexError:
            logging.debug(f"missing translation index at {frame}")
            pass

    @staticmethod
    def scale(target, data, frame):
        try:
            for landmark in data:
                target[landmark[0]].scale = Vector((landmark[1]))
                target[landmark[0]].keyframe_insert(data_path="scale", frame=frame)
        except IndexError:
            logging.debug(f"missing scale index at {data}, {frame}")
            pass

    @staticmethod
    def quaternion_rotate(target, data, frame):
        """ Translates and keyframes bpy empty objects. """
        try:
            for landmark in data:
                target[landmark[0]].rotation_quaternion = landmark[1]
                target[landmark[0]].keyframe_insert(data_path="rotation_quaternion", frame=frame)
        except IndexError:
            logging.debug(f"missing quat_euler_rotate index {data}, {frame}")
            pass

    def euler_rotate(self, target, data, frame, idx_offset=0):
        """ Translates and keyframes bpy empty objects. """
        try:
            for landmark in data:
                target[landmark[0]].rotation_euler = landmark[1]
                target[landmark[0]].keyframe_insert(data_path="rotation_euler", frame=frame)
                self.prev_rotation[landmark[0] + idx_offset] = landmark[1]
        except IndexError:
            logging.debug(f"missing euler_rotate index at {data}, {frame}")
            pass