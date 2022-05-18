from ..cgt_blender.utils import objects
from ..cgt_naming import HAND, COLLECTIONS
from . import bpy_instance_provider


class BpyHandReferences(bpy_instance_provider.BpyInstanceProvider):
    references = {
        # receiver objects
        0:  HAND.wrist,
        1:  HAND.thumb_cmc,
        2:  HAND.thumb_mcp,
        3:  HAND.thumb_ip,
        4:  HAND.thumb_tip,
        5:  HAND.index_finger_mcp,
        6:  HAND.index_finger_pip,
        7:  HAND.index_finger_dip,
        8:  HAND.index_finger_tip,
        9:  HAND.middle_finger_mcp,
        10: HAND.middle_finger_pip,
        11: HAND.middle_finger_dip,
        12: HAND.middle_finger_tip,
        13: HAND.ring_finger_mcp,
        14: HAND.ring_finger_pip,
        15: HAND.ring_finger_dip,
        16: HAND.ring_finger_tip,
        17: HAND.pinky_mcp,
        18: HAND.pinky_pip,
        19: HAND.pinky_dip,
        20: HAND.pinky_tip,

        # driver objects
        21: HAND.driver_thumb_cmc,
        22: HAND.driver_thumb_mcp,
        23: HAND.driver_thumb_ip,
        24: HAND.driver_thumb_tip,
        25: HAND.driver_index_finger_mcp,
        26: HAND.driver_index_finger_pip,
        27: HAND.driver_index_finger_dip,
        28: HAND.driver_index_finger_tip,
        29: HAND.driver_middle_finger_mcp,
        30: HAND.driver_middle_finger_pip,
        31: HAND.driver_middle_finger_dip,
        32: HAND.driver_middle_finger_tip,
        33: HAND.driver_ring_finger_mcp,
        34: HAND.driver_ring_finger_pip,
        35: HAND.driver_ring_finger_dip,
        36: HAND.driver_ring_finger_tip,
        37: HAND.driver_pinky_mcp,
        38: HAND.driver_pinky_pip,
        39: HAND.driver_pinky_dip,
        40: HAND.driver_pinky_tip,
    }
    fingers = [
        [1, 5],  # thumb
        [5, 9],  # index finger
        [9, 13],  # middle finger
        [13, 17],  # ring finger
        [17, 21],  # pinky
    ]

    # hands
    left_hand = []
    right_hand = []
    col_name = COLLECTIONS.hands
    parent_col = COLLECTIONS.drivers

    def __init__(self):
        self.left_hand = objects.add_empties(self.references, 0.005, ".L")
        self.right_hand = objects.add_empties(self.references, 0.005, ".R")
        objects.add_list_to_collection(self.col_name, self.left_hand, self.parent_col)
        objects.add_list_to_collection(self.col_name, self.right_hand, self.parent_col)

    def get_instances(self):
        return self.left_hand, self.right_hand

    def set_position(self, data, frame):
        """ Keyframes input data."""
        left_hand_data, right_hand_data = data
        for hand in [[self.left_hand, left_hand_data],
                     [self.right_hand, right_hand_data]]:
            try:
                self.translate(hand[0], hand[1], frame)
            except IndexError:
                pass

    def set_rotation(self, data, frame):
        left_angles, right_angles = data
        """ Keyframes custom angle data. """
        # [hand drivers, hand angles, euler combat idx offset]
        for hand in [[self.left_hand, left_angles, 0],
                     [self.right_hand, right_angles, 100]]:
            try:
                if hand[1] is None:
                    break

                self.euler_rotate(hand[0], hand[1], frame, hand[2])
            except IndexError:
                pass