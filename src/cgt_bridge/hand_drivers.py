import numpy as np
from mathutils import Euler

from . import abs_assignment
from ..cgt_blender.utils import objects
from ..cgt_naming import HAND, COLLECTIONS
from ..cgt_utils import m_V
from math import degrees


class BridgeHand(abs_assignment.DataAssignment):
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

    max_values = [-155] * 20
    min_values = [155] * 20
    avg_values = []

    # hands
    left_hand = []
    right_hand = []

    #  position and joint angle
    left_hand_data, right_hand_data = None, None
    left_angles, right_angles = None, None

    frame = 0
    col_name = COLLECTIONS.hands

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
                if hand[1] is None:
                    break

                self.euler_rotate(hand[0], hand[1], self.frame, hand[2])
            except IndexError:
                pass

    def finger_angles(self, hand):
        """ get finger joint x-angles of target hand """
        if hand == []:
            return None

        x_angles = self.get_x_angles(hand)
        z_angles = self.get_y_angles(hand)

        data = []
        for idx in range(0, 20):
            if x_angles[idx] != 0 or z_angles[idx] != 0:
                joint_angle = [idx, Euler((x_angles[idx], 0, z_angles[idx]))]
                data.append(joint_angle)

        # self.print_angle_matrix(x_angles)
        return data

    def print_angle_matrix(self, angles):
        # printing matrix for setting up drivers
        deg = [degrees(d) for d in angles]

        # averages
        avg_container = [0]*20
        self.avg_values.append(deg)
        for values in self.avg_values:
            for i, val in enumerate(values):
                avg_container[i] += val
        avg_c = [val / len(self.avg_values) for val in avg_container]
        print(f"{len(self.avg_values)}, \n")

        # current
        for finger in self.fingers:
            cu = [[idx, self.min_values[idx], avg_c[idx], deg[idx], self.max_values[idx]] for idx in
                  range(finger[0], finger[1] - 1)]
            print(cu)

        # min max values
        for idx, d in enumerate(deg):
            if d > self.max_values[idx]:
                self.max_values[idx] = d
            if d < self.min_values[idx]:
                self.min_values[idx] = d

    def get_y_angles(self, hand):
        """ get approximate y angle
            by projecting the proximal phalanges on a plane
            taking the vector from wrist to knuckle
            and calculating the angle offset."""
        proximal = [idx[0] + 1 for idx in self.fingers]
        joints = np.array([[0, 1, 2]])
        data = [0] * 20

        plane = np.array([
            hand[0][1],
            hand[1][1] * 25,
            hand[17][1] * 25
        ])

        # project proximal phalanges on plane based on surrounding metacarpals
        for idx, carpal in enumerate(self.fingers):
            # project per knuckle
            # plane = np.array([hand[0][1],
            #                   hand[carpal[0]][1] * 25,      # mcp
            #                   hand[carpal[1]-1][1] * 25])   # tip

            projection = m_V.project_vec_on_plane(
                plane,
                joints,
                np.array(hand[proximal[idx]][1])
            )

            proj_carpal = m_V.project_vec_on_plane(
                plane,
                joints,
                np.array(hand[carpal[0]][1])
            )
            angle = m_V.angle_between(np.array(projection), np.array(proj_carpal))

            # get angle between projected vector and knuckle
            # angle = m_V.angle_between(np.array(projection), np.array(hand[carpal[0]][1]))

            if angle is None:
                break
            data[carpal[0]] = angle
        return data

    def get_x_angles(self, hand):
        """ get finger x angle by calculating the angle between each finger joint """
        origin = hand[0][1]  # [0, 0, 0]
        # finger vertices - wrist as origin to fingers
        fingers = [[hand[idx][1] for idx in range(finger[0], finger[1])] for finger in self.fingers]
        fingers = [np.array([origin] + finger) for finger in fingers]

        # setup joints to calc finger angles
        x_joints = [[0, 1, 2], [1, 2, 3], [2, 3, 4]]
        x_finger_angles = [m_V.joint_angles(finger, x_joints) for finger in fingers]

        data = [0] * 20
        for idx, angles in enumerate(x_finger_angles):
            if angles is None:
                break
            # finger start & end idx
            mcp, tip = self.fingers[idx]
            # iter over every finger joint
            for angle_idx, finger_idx in enumerate(range(mcp, tip - 1)):
                data[finger_idx] = angles[angle_idx]

        return data

    def global_hand_rotation(self, hand, combat_idx_offset=0, orientation="R"):
        """ calculates approximate hand rotation by generating
            a matrix using the palm as approximate triangle. """
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
