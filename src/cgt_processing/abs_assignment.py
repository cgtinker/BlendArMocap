from abc import ABC, abstractmethod
from math import pi
import numpy as np
from mathutils import Euler

from ..cgt_utils import m_V


class DataProcessor(ABC):
    data = None

    # array for comparison, as noise is present every frame values should change
    frame = 0
    prev_rotation = {}
    prev_sum = 0.0

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

    # region duplicates
    def has_duplicated_results(self, data=None):
        """ Sums data array values and compares them each frame to avoid duplicated values
            in the timeline. This fixes duplicated frame issue mainly occurring on Windows. """
        summed = np.sum([v[1] for v in data[:21]])
        if summed == self.prev_sum:
            print("skipping duplicate keyframe", self.frame)
            return True

        self.prev_sum = summed
        return False
    # endregion

    # region bpy object oriented
    def quart_to_euler_combat(self, quart, idx, idx_offset=0, axis='XYZ'):
        """ Converts quart to euler rotation while comparing with previous rotation. """
        if len(self.prev_rotation) > 0:
            try:
                combat = self.prev_rotation[idx + idx_offset]
                return m_V.to_euler(quart, combat, axis)
            except KeyError:
                print(f"invalid id to euler combat {idx}, {self.frame}")
                return m_V.to_euler(quart)
        else:
            return m_V.to_euler(quart)

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
                m_rot = m_V.to_euler(
                    quart_rotation,
                    self.prev_rotation[prev_rot_idx]
                )

            else:
                # -offset for combat
                tmp_offset = [-o for o in offset]
                m_rot = m_V.to_euler(
                    quart_rotation,
                    self.offset_euler(self.prev_rotation[prev_rot_idx], tmp_offset)
                )

        except KeyError:
            m_rot = m_V.to_euler(quart_rotation)

        return self.offset_euler(m_rot, offset)
    # endregion
