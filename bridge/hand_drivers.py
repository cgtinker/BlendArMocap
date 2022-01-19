import importlib

import numpy as np
from mathutils import Euler, Quaternion
from math import pi

from blender import objects
from bridge import abs_assignment
from utils import m_V

importlib.reload(objects)
importlib.reload(abs_assignment)
importlib.reload(m_V)


class BridgeHand(abs_assignment.DataAssignment):
    references = {
        0: "cgt_WRIST",
        1: "cgt_THUMB_CMC",
        2: "cgt_THUMB_MCP",
        3: "cgt_THUMP_IP",
        4: "cgt_THUMB_TIP",
        5: "cgt_INDEX_FINGER_MCP",
        6: "cgt_INDEX_FINGER_PIP",
        7: "cgt_INDEX_FINGER_DIP",
        8: "cgt_INDEX_FINGER_TIP",
        9: "cgt_MIDDLE_FINGER_MCP",
        10: "cgt_MIDDLE_FINGER_PIP",
        11: "cgt_MIDDLE_FINGER_DIP",
        12: "cgt_MIDDLE_FINGER_TIP",
        13: "cgt_RING_FINGER_MCP",
        14: "cgt_RING_FINGER_PIP",
        15: "cgt_RING_FINGER_DIP",
        16: "cgt_RING_FINGER_TIP",
        17: "cgt_PINKY_MCP",
        18: "cgt_PINKY_PIP",
        19: "cgt_PINKY_DIP",
        20: "cgt_PINKY_TIP"
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
    col_name = "cgt_hands"

    def init_references(self):
        """ generate empty objects for mapping. """
        self.left_hand = objects.add_empties(self.references, 0.005, ".L")
        self.right_hand = objects.add_empties(self.references, 0.005, ".R")
        objects.add_list_to_collection(self.col_name, self.left_hand, self.driver_col)
        objects.add_list_to_collection(self.col_name, self.right_hand, self.driver_col)

    def init_data(self):
        self.left_hand_data, self.right_hand_data = self.landmarks_to_hands(list(zip(self.data[0], self.data[1])))
        self.left_angles = self.finger_angles(self.left_hand_data)
        self.right_angles = self.finger_angles(self.right_hand_data)

    def update(self):
        self.set_position()

        # updated angle to joint references before applying
        self.left_angles = self.prepare_rotation_data(self.left_angles)
        self.right_angles = self.prepare_rotation_data(self.right_angles)

        # using bpy matrix
        left_hand_rot = self.global_hand_rotation(self.left_hand_data, 0, "L")
        if left_hand_rot != None:
            self.left_angles.append(left_hand_rot)

        right_hand_rot = self.global_hand_rotation(self.right_hand_data, 100, "R") # offset for euler combat
        if right_hand_rot != None:
            self.right_angles.append(right_hand_rot)

        self.set_rotation()

    def set_position(self):
        """ keyframe the input data."""
        for hand in [[self.left_hand, self.left_hand_data],
                     [self.right_hand, self.right_hand_data]]:
            try:
                self.translate(hand[0], hand[1], self.frame)
            except IndexError:
                pass

    def set_rotation(self):
        """ keyframe custom angle data """
        # [hand drivers, hand angles, euler combat idx offset]
        for hand in [[self.left_hand, self.left_angles, 0],
                     [self.right_hand, self.right_angles, 100]]:
            try:
                self.euler_rotate(hand[0], hand[1], self.frame, hand[2])
            except IndexError:
                pass

    def prepare_rotation_data(self, angle_data):
        """ prepare data formatting for applying keyframe """
        data = []
        # check if contains agnles
        if angle_data is None:
            return data

        # every angle targets a finger joint
        for idx, angles in enumerate(angle_data):
            if angles is None:
                break

            # finger start & end idx
            mcp, tip = self.fingers[idx]
            # iter over every finger joint
            for angle_idx, finger_idx in enumerate(range(mcp, tip - 1)):
                joint_angle = [finger_idx, Euler((angles[angle_idx], 0, 0))]
                data.append(joint_angle)

        return data

    def finger_angles(self, hand):
        """ get finger joint angles of target hand """
        if hand == []:
            return None

        # get all finger vertex positions and add the origin
        origin = hand[0][1]  # [0, 0, 0]
        fingers = [[hand[idx][1] for idx in range(finger[0], finger[1])] for finger in self.fingers]
        fingers = [np.array([origin] + finger) for finger in fingers]  # add origin to finger

        # setup joints to calc finger angles
        joints = [[0, 1, 2], [1, 2, 3], [2, 3, 4]]
        finger_angles = [m_V.joint_angles(finger, joints) for finger in fingers]
        return finger_angles

    def global_hand_rotation(self, hand, combat_idx_offset=0, orientation="R"):
        if hand == []:
            return None

        palm_center = m_V.center_point(hand[5][1], hand[17][1])

        # generate triangle
        vertices = np.array(
            [hand[0][1],
             hand[5][1],
             hand[17][1]])
        connections = np.array([[0, 1, 2]])

        # normal from triangle
        normal, norm = m_V.create_normal_array(vertices, connections)
        normal = m_V.normalize(normal[0])

        # origin to palm center
        tangent = m_V.normalize(m_V.to_vector(
            hand[0][1],
            palm_center
        ))

        # palm dir
        binormal = m_V.normalize(m_V.to_vector(
            hand[5][1],
            hand[17][1]
        ))

        # rotation from matrix
        matrix = m_V.generate_matrix(normal, tangent, binormal)
        loc, quart, sca = m_V.decompose_matrix(matrix)

        # euler = self.quart_to_euler_combat(quart, 0, combat_idx_offset)
        # euler = m_V.to_euler(quart)

        if orientation == "R":
            # euler = Euler((euler[0] - pi * .5, euler[2] + pi * .5, euler[1]))
            offset = [-.5, .5, 0]
            euler = self.try_get_euler(quart, offset, combat_idx_offset)
            euler = self.offset_euler(euler, offset)

        else:
            offset = [-.5, -.5, 0]
            euler = self.try_get_euler(quart, offset, combat_idx_offset)
            euler = self.offset_euler(euler, offset)
            # euler = Euler((euler[0] - pi * .5, euler[2]-pi*.5, euler[1]))

        hand_rotation = ([0, euler])
        return hand_rotation

    def landmarks_to_hands(self, hand_data):
        """ determines where the data belongs to """
        left_hand = [data[0] for data in hand_data if data[1][1] is False]
        right_hand = [data[0] for data in hand_data if data[1][1] is True]

        left_hand = self.set_global_origin(left_hand)
        right_hand = self.set_global_origin(right_hand)

        return left_hand, right_hand

    @staticmethod
    def set_global_origin(data):
        if len(data) > 0:
            data = [[idx, np.array([-lmrk[0], lmrk[2], -lmrk[1]])] for idx, lmrk in data[0]]
            data = [[idx, lmrk - data[0][1]] for idx, lmrk in data]
        return data
