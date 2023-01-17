import numpy as np
import logging
from mathutils import Euler
from . import cgt_math


class CustomData:
    idx = None
    loc = None
    rot = None
    sca = None

    def __init__(self, idx):
        self.idx = idx


class ProcessorUtils:
    data = None
    # array for comparison, as noise is present every frame values should change
    frame = 0
    prev_rotation = {}
    prev_sum = [0.0, 0.0]

    def has_duplicated_results(self, data=None, detector_type=None, idx=0):
        """ Sums data array values and compares them each frame to avoid duplicated values
            in the timeline. This fixes duplicated frame issue mainly occurring on Windows. """
        summed = np.sum([v[1] for v in data[:21]])
        if summed == self.prev_sum[idx]:
            return True

        self.prev_sum[idx] = summed
        return False

    def quart_to_euler_combat(self, quart, idx, idx_offset=0, axis='XYZ'):
        """ Converts quart to euler rotation while comparing with previous rotation. """
        if len(self.prev_rotation) > 0:
            try:
                combat = self.prev_rotation[idx + idx_offset]
                return cgt_math.to_euler(quart, combat, axis)
            except KeyError:
                logging.debug(f"Invalid id to euler combat {idx}, {self.frame}")
                return cgt_math.to_euler(quart)
        else:
            return cgt_math.to_euler(quart)

    @staticmethod
    def offset_euler(euler, offset: list = None):
        """ Offsets an euler rotation using euler radians *pi. """
        if offset is None:
            return euler

        rotation = Euler((
            euler[0] + np.pi * offset[0],
            euler[1] + np.pi * offset[1],
            euler[2] + np.pi * offset[2],
        ))
        return rotation

    def try_get_euler(self, quart_rotation, offset: list = None, prev_rot_idx: int = None):
        """ Gets an euler rotation from quaternion with using the previously
            created rotation as combat to avoid discontinuity. """
        if prev_rot_idx is None:
            return cgt_math.to_euler(quart_rotation)

        # initialize prev rotation
        elif prev_rot_idx not in self.prev_rotation:
            self.prev_rotation[prev_rot_idx] = cgt_math.to_euler(quart_rotation)
            return self.prev_rotation[prev_rot_idx]

        # get euler with combat
        if offset is None:
            euler_rot = cgt_math.to_euler(
                quart_rotation,
                self.prev_rotation[prev_rot_idx]
            )
            self.prev_rotation[prev_rot_idx] = euler_rot
            return self.prev_rotation[prev_rot_idx]

        else:
            tmp_offset = [-o for o in offset]
            euler_rot = cgt_math.to_euler(
                quart_rotation,
                self.offset_euler(self.prev_rotation[prev_rot_idx], tmp_offset)
            )

            self.prev_rotation[prev_rot_idx] = self.offset_euler(euler_rot, offset)
            return self.prev_rotation[prev_rot_idx]

