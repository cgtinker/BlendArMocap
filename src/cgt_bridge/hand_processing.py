from math import degrees

import numpy as np
from mathutils import Euler

from . import abs_assignment
from ..cgt_blender.utils import objects
from ..cgt_naming import HAND, COLLECTIONS
from ..cgt_utils import m_V


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
        if self.has_duplicated_results(self.right_hand_data):
            return

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
        z_angles = self.get_z_angles(hand)

        data = []
        for idx in range(0, 20):
            if x_angles[idx] != 0 or z_angles[idx] != 0:
                joint_angle = [idx, Euler((x_angles[idx], 0, z_angles[idx]))]
                data.append(joint_angle)

        # self.print_angle_matrix(z_angles)
        return data

    def print_angle_matrix(self, angles):
        # printing matrix for setting up drivers
        deg = [degrees(d) for d in angles]

        # current
        for finger in self.fingers:
            cu = [[idx, self.min_values[idx], deg[idx], self.max_values[idx]] for idx in
                  range(finger[0], finger[1] - 1)]
            print(cu)

        # min max values
        for idx, d in enumerate(deg):
            if d > self.max_values[idx]:
                self.max_values[idx] = d
            if d < self.min_values[idx]:
                self.min_values[idx] = d

    def get_z_angles(self, hand):
        """ Project finger mcps on a vector between index and pinky mcp.
            Create circles around the mcps circles facing in the direction of vectors depending on the palm.
            Searching for the closest point on the circle to the fingers dip and calculate the angle.
            Thumb gets projected on a plane between thumb mcp, index mcp and wrist to calculate the z-angle.
        """
        data = [0] * 20
        joints = np.array([[0, 1, 2]])

        def calculate_thumb_angle():
            # create plane to project thumb mcp & pip on plane
            plane = np.array([np.array([0, 0, 0]), hand[1][1], hand[5][1]])
            thumb_proj = [m_V.project_vec_on_plane(plane, joints, p)
                          for p in [hand[1][1], hand[5][1], hand[2][1]]]

            # vectors to calculate angle
            thumb_vecs = [m_V.to_vector(tp[0], tp[1]) for tp in [
                [thumb_proj[0], thumb_proj[1]],
                [thumb_proj[0], thumb_proj[2]]]]

            return m_V.angle_between(np.array(thumb_vecs[0]), np.array(thumb_vecs[1]))

        data[1] = calculate_thumb_angle()

        # calculate other finger angles
        tangent = m_V.to_vector(np.array(hand[5][1]), np.array(hand[17][1]))
        # get pips, mcps and their dists (mcps projected on tangent)
        mcps = [m_V.project_point_on_vector(
            np.array(hand[finger[0]][1]), np.array(hand[5][1]), np.array(hand[17][1]))
            for finger in self.fingers[1:]]
        pips = [np.array(hand[finger[1] - 2][1]) for finger in self.fingers[1:]]
        dists = [m_V.get_vector_distance(mcps[i], pips[i]) for i in range(0, 4)]

        # circle direction vectors related to the hand to calc angles
        pinky_vec = m_V.to_vector(np.array(hand[0][1]), np.array(hand[17][1]))
        thumb_vec = m_V.to_vector(np.array(hand[1][1]), np.array(hand[5][1]))
        dirs = [pinky_vec, pinky_vec, thumb_vec, thumb_vec]

        points = 20
        for i in range(0, 4):
            # circle around tangent in target dir
            circle = m_V.create_circle_around_vector(tangent, mcps[i], dists[i], points, dirs[i])
            closest = m_V.get_closest_idx(pips[i], circle)

            # angle between the closest point on circle to mcp and pip to mcp vectors
            mcp_pip = m_V.to_vector(mcps[i], pips[i])
            mcp_closest = m_V.to_vector(mcps[i], circle[closest])

            # todo: check for pos / negative
            expanded_circle = circle + circle + circle
            a = expanded_circle[closest + points + 6]
            b = expanded_circle[closest + points - 6]

            plane = np.array([a, circle[closest], b])
            normal = m_V.normal_from_plane(plane)
            # normal, norm = m_V.create_normal_array(np.array(plane), np.array(joints))
            normal = m_V.normalize(normal)
            dist = m_V.distance_from_plane(pips[i], normal, circle[closest])
            # print("dist", dist, "norm", normal)

            angle = m_V.angle_between(np.array(mcp_pip), np.array(mcp_closest))
            if dist < 0:
                angle = -angle
                print("RDC DIST", dist, angle, normal)
            else:
                print("NRM DIST", dist, angle)

            data[self.fingers[i + 1][0]] = angle

        return data

    def get_x_angles(self, hand):
        """ get finger x angle by calculating the angle between each finger joint """
        # finger vertices - wrist as origin to fingers
        fingers = [[hand[idx][1] for idx in range(finger[0], finger[1])] for finger in self.fingers]
        fingers = [np.array([np.array([0, 0, 0])] + finger) for finger in fingers]

        joints = np.array([[0, 1, 2]])
        # straighten fingers by plane projection
        for idx, finger in enumerate(fingers):
            plane = np.array([np.array([0, 0, 0]), finger[1], finger[4]])
            f = [m_V.project_vec_on_plane(plane, joints, p) for p in finger]
            fingers[idx] = f

        # setup joints to calc finger angles
        x_joints = [[0, 1, 2], [1, 2, 3], [2, 3, 4]]
        x_finger_angles = [m_V.joint_angles(finger, x_joints) for finger in fingers]

        data = [0] * 20
        for idx, angles in enumerate(x_finger_angles):
            if angles is None:
                break
            # iter over every finger joint and calc angle
            mcp, tip = self.fingers[idx]
            for angle_idx, finger_idx in enumerate(range(mcp, tip - 1)):
                data[finger_idx] = angles[angle_idx]

        return data

    def global_hand_rotation(self, hand, combat_idx_offset=0, orientation="R"):
        """ calculates approximate hand rotation by generating
            a matrix using the palm as approximate triangle. """
        if hand == []:
            return None

        if orientation == "R":
            rotation = [-60, 60, 0]
        else:
            rotation = [-60, -60, 0]

        rotated_points = [m_V.rotate_point_euler(np.array(hand[idx][1]), rotation) for idx in [1, 5, 13]]

        # setup vectors to create an matrix
        tangent = m_V.normalize(m_V.to_vector(
            rotated_points[0],
            rotated_points[1]
        ))
        binormal = m_V.normalize(m_V.to_vector(
            rotated_points[1],
            rotated_points[2]
        ))
        normal = m_V.normalize(np.cross(binormal, tangent))

        # rotation from matrix
        matrix = m_V.generate_matrix(normal, tangent, binormal)
        loc, quart, sca = m_V.decompose_matrix(matrix)

        euler = self.try_get_euler(quart, offset=[0, 0, 0], prev_rot_idx=combat_idx_offset)
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
