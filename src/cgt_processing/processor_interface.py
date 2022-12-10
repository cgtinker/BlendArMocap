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

from abc import ABC, abstractmethod
from math import pi
import numpy as np
from mathutils import Euler

from ..cgt_utils import cgt_math


class DataProcessor(ABC):
    data = None

    # array for comparison, as noise is present every frame values should change
    frame = 0
    prev_rotation = {}
    prev_sum = [0.0, 0.0]

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
    def init_print(self):
        """ mainly for printing processed data. (ignoring bpy mathutils). """
        pass

    @abstractmethod
    def update(self):
        """ updates every mp solution received. """
        pass
    # endregion

    # region duplicates
    def has_duplicated_results(self, data=None, detector_type=None, idx=0):
        """ Sums data array values and compares them each frame to avoid duplicated values
            in the timeline. This fixes duplicated frame issue mainly occurring on Windows. """
        summed = np.sum([v[1] for v in data[:21]])
        if summed == self.prev_sum[idx]:
            print("skipping duplicate keyframe", self.frame, detector_type)
            return True

        self.prev_sum[idx] = summed
        return False
    # endregion

    # region bpy object oriented
    def quart_to_euler_combat(self, quart, idx, idx_offset=0, axis='XYZ'):
        """ Converts quart to euler rotation while comparing with previous rotation. """
        if len(self.prev_rotation) > 0:
            try:
                combat = self.prev_rotation[idx + idx_offset]
                return cgt_math.to_euler(quart, combat, axis)
            except KeyError:
                print(f"invalid id to euler combat {idx}, {self.frame}")
                return cgt_math.to_euler(quart)
        else:
            return cgt_math.to_euler(quart)

    @staticmethod
    def offset_euler(euler, offset: []):
        """ Offsets an euler rotation using euler radians *pi. """
        rotation = Euler((
            euler[0] + pi * offset[0],
            euler[1] + pi * offset[1],
            euler[2] + pi * offset[2],
        ))
        return rotation

    def try_get_euler(self, quart_rotation, offset: [], prev_rot_idx: int = -1):
        """ Gets an euler rotation from quaternion with using the previously
            created rotation as combat to avoid discontinuity. """

        try:
            if offset == None:
                m_rot = cgt_math.to_euler(
                    quart_rotation,
                    self.prev_rotation[prev_rot_idx]
                )

            else:
                # -offset for combat
                tmp_offset = [-o for o in offset]
                m_rot = cgt_math.to_euler(
                    quart_rotation,
                    self.offset_euler(self.prev_rotation[prev_rot_idx], tmp_offset)
                )

        except KeyError:
            m_rot = cgt_math.to_euler(quart_rotation)

        return self.offset_euler(m_rot, offset)
    # endregion
