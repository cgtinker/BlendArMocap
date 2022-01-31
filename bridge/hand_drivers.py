import importlib

import numpy as np
from mathutils import Euler

import m_CONST
from _blender.utils import objects
from bridge import abs_assignment
from utils import m_V

importlib.reload(objects)
importlib.reload(abs_assignment)
importlib.reload(m_V)
importlib.reload(m_CONST)


class BridgeHand(abs_assignment.DataAssignment):
    references = {
        0: m_CONST.HAND.wrist.value,
        1: m_CONST.HAND.thumb_cmc.value,
        2: m_CONST.HAND.thumb_mcp.value,
        3: m_CONST.HAND.thumb_ip.value,
        4: m_CONST.HAND.thumb_tip.value,
        5: m_CONST.HAND.index_finger_mcp.value,
        6: m_CONST.HAND.index_finger_pip.value,
        7: m_CONST.HAND.index_finger_dip.value,
        8: m_CONST.HAND.index_finger_tip.value,
        9: m_CONST.HAND.middle_finger_mcp.value,
        10: m_CONST.HAND.middle_finger_pip.value,
        11: m_CONST.HAND.middle_finger_dip.value,
        12: m_CONST.HAND.middle_finger_tip.value,
        13: m_CONST.HAND.ring_finger_mcp.value,
        14: m_CONST.HAND.ring_finger_pip.value,
        15: m_CONST.HAND.ring_finger_dip.value,
        16: m_CONST.HAND.ring_finger_tip.value,
        17: m_CONST.HAND.pinky_mcp.value,
        18: m_CONST.HAND.pinky_pip.value,
        19: m_CONST.HAND.pinky_dip.value,
        20: m_CONST.HAND.pinky_tip.value,
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
    col_name = m_CONST.COLLECTIONS.hands.value

    def init_references(self):
        """ generate empty objects for mapping. """
        self.left_hand = objects.add_empties(self.references, 0.005, ".L")
        self.right_hand = objects.add_empties(self.references, 0.005, ".R")
        objects.add_list_to_collection(self.col_name, self.left_hand, self.driver_col)
        objects.add_list_to_collection(self.col_name, self.right_hand, self.driver_col)

    def init_data(self):
        """ prepares data before setting """
        self.left_hand_data, self.right_hand_data = self.landmarks_to_hands(list(zip(self.data[0], self.data[1])))
        self.left_angles = self.finger_angles(self.left_hand_data)
        self.right_angles = self.finger_angles(self.right_hand_data)

        # updated angle to joint references before applying
        self.left_angles = self.prepare_rotation_data(self.left_angles)
        self.right_angles = self.prepare_rotation_data(self.right_angles)

        # using bpy matrix
        left_hand_rot = self.global_hand_rotation(self.left_hand_data, 0, "L")
        if left_hand_rot != None:
            self.left_angles.append(left_hand_rot)

        right_hand_rot = self.global_hand_rotation(self.right_hand_data, 100, "R")  # offset for euler combat
        if right_hand_rot != None:
            self.right_angles.append(right_hand_rot)

    def update(self):
        """ applies gathered data to references """
        self.set_position()
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
        """ get finger joint x-angles of target hand """
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
        """calculates approximate hand rotation. """
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
            palm_center,
            hand[17][1]
        ))

        # rotation from matrix
        matrix = m_V.generate_matrix(normal, tangent, binormal)
        loc, quart, sca = m_V.decompose_matrix(matrix)

        offset = [0, 0, 0]
        euler = self.try_get_euler(quart, offset, combat_idx_offset)
        euler = self.offset_euler(euler, offset)

        hand_rotation = ([0, euler])
        return hand_rotation

    def landmarks_to_hands(self, hand_data):
        """ determines to which hand the landmark data belongs """
        left_hand = [data[0] for data in hand_data if data[1][1] is False]
        right_hand = [data[0] for data in hand_data if data[1][1] is True]

        left_hand = self.set_global_origin(left_hand)
        right_hand = self.set_global_origin(right_hand)

        return left_hand, right_hand

    @staticmethod
    def set_global_origin(data):
        """ sets global origin of landmarks to wrist """
        if len(data) > 0:
            data = [[idx, np.array([-lmrk[0], lmrk[2], -lmrk[1]])] for idx, lmrk in data[0]]
            data = [[idx, lmrk - data[0][1]] for idx, lmrk in data]
        return data
