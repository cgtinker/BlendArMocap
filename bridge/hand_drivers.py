import importlib

import numpy as np
from mathutils import Euler

from blender import objects
from bridge import abs_assignment
from utils import m_V

importlib.reload(objects)
importlib.reload(abs_assignment)
importlib.reload(m_V)


class BridgeHand(abs_assignment.DataAssignment):
    references = {
        0: "WRIST",
        1: "THUMB_CMC",
        2: "THUMB_MCP",
        3: "THUMP_IP",
        4: "THUMB_TIP",
        5: "INDEX_FINGER_MCP",
        6: "INDEX_FINGER_PIP",
        7: "INDEX_FINGER_DIP",
        8: "INDEX_FINGER_TIP",
        9: "MIDDLE_FINGER_MCP",
        10: "MIDDLE_FINGER_PIP",
        11: "MIDDLE_FINGER_DIP",
        12: "MIDDLE_FINGER_TIP",
        13: "RING_FINGER_MCP",
        14: "RING_FINGER_PIP",
        15: "RING_FINGER_DIP",
        16: "RING_FINGER_TIP",
        17: "PINKY_MCP",
        18: "PINKY_PIP",
        19: "PINKY_DIP",
        20: "PINKY_TIP"
    }
    fingers = [
        [5, 9],  # index finger
        [9, 13],  # middle finger
        [13, 17],  # ring finger
        [17, 21],  # pinky
        [1, 5]  # thumb
    ]

    # hands
    left_hand = []
    right_hand = []

    #  position and joint angle
    left_hand_data, right_hand_data = None, None
    left_angles, right_angles = None, None

    frame = 0
    col_name = "Hands"
    col_diver = "Hand_Divers"

    def __init__(self, mode='realtime'):
        self.right_driver = abs_assignment.CustomData()
        self.left_driver = abs_assignment.CustomData()
        self.init_references()

    def init_references(self):
        """ generate empty objects for mapping. """
        self.left_hand = objects.add_empties(self.references, 0.005, ".L")
        self.right_hand = objects.add_empties(self.references, 0.005, ".R")
        objects.add_list_to_collection(self.col_name, self.left_hand)
        objects.add_list_to_collection(self.col_name, self.right_hand)

        self.init_driver_obj(
            self.right_driver, self.right_hand, 0.025, "right_hand", "CIRCLE", [.25, 0, 0],
            is_parent=True, children=self.right_hand)

        self.init_driver_obj(
            self.left_driver, self.left_hand, 0.025, "left_hand", "CIRCLE", [-.25, 0, 0],
            is_parent=True, children=self.left_hand)

    def init_data(self):
        self.left_hand_data, self.right_hand_data = self.landmarks_to_hands(list(zip(self.data[0], self.data[1])))
        self.left_angles = self.finger_angles(self.left_hand_data)
        self.right_angles = self.finger_angles(self.right_hand_data)

    def update(self):
        self.set_position()

        # updated angle to joint references before applying
        self.left_angles = self.prepare_rotation_data(self.left_angles)
        self.right_angles = self.prepare_rotation_data(self.right_angles)
        self.set_rotation()

    def set_position(self):
        """ keyframe the input data."""
        for hand in [[self.left_hand, self.left_hand_data], [self.right_hand, self.right_hand_data]]:
            try:
                self.translate(hand[0], hand[1], self.frame)
            except IndexError:
                pass

    def set_rotation(self):
        """ keyframe custom angle data """
        for hand in [[self.left_hand, self.left_angles], [self.right_hand, self.right_angles]]:
            try:
                self.euler_rotate(hand[0], hand[1], self.frame)
            except IndexError:
                pass

    def prepare_rotation_data(self, angle_data):
        """ prepare data format before applying keyframe """
        data = []

        if angle_data is None:
            return data

        for idx, angles in enumerate(angle_data):
            if angles is None:
                break

            mcp, tip = self.fingers[idx]
            for angle_idx, finger_idx in enumerate(range(mcp, tip - 1)):
                joint_angle = [finger_idx, Euler((angles[angle_idx], 0, 0))]
                data.append(joint_angle)

        return data

    def finger_angles(self, hand):
        """ get finger joint angles of target hand """
        if hand == []:
            return None

        origin = hand[0][1]
        fingers = [[hand[idx][1] for idx in range(finger[0], finger[1])] for finger in self.fingers]
        fingers = [np.array([origin] + finger) for finger in fingers]

        joints = [[0, 1, 2], [1, 2, 3], [2, 3, 4]]
        finger_angles = [m_V.joint_angles(finger, joints) for finger in fingers]
        return finger_angles

    def landmarks_to_hands(self, hand_data):
        """ determines where the data belongs to """
        left_hand = [data[0] for data in hand_data if data[1][1] is True]
        right_hand = [data[0] for data in hand_data if data[1][1] is False]

        left_hand = self.set_global_origin(left_hand)
        right_hand = self.set_global_origin(right_hand)

        return left_hand, right_hand

    @staticmethod
    def set_global_origin(data):
        if len(data) > 0:
            data = [[idx, np.array([-lmrk[0], lmrk[2], -lmrk[1]])] for idx, lmrk in data[0]]
            data = [[idx, lmrk - data[0][1]] for idx, lmrk in data]
        return data
