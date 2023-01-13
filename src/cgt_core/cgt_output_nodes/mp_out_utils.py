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