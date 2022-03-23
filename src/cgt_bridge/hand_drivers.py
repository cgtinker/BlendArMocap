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
        # if self.has_duplicated_results(self.left_hand_data[0][0]):
        #     return

        self.set_position()
        self.set_rotation()

        # self.prev_data = self.left_hand_data[0][0]

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
        z_angles = self.get_y_angles_circular(hand)

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

    def get_y_angles_circular(self, hand):
        joints = np.array([[0, 1, 2]])
        data = [0] * 20

        # create plane to calc thumb angle
        plane = np.array([np.array([0, 0, 0]), hand[1][1], hand[5][1]])

        # project mcps & pip on plane
        proj_mcp = m_V.project_vec_on_plane(plane, joints, hand[1][1])
        proj_mcp_b = m_V.project_vec_on_plane(plane, joints, hand[5][1])
        proj_pip = m_V.project_vec_on_plane(plane, joints, np.array(hand[2][1]))

        # vectors for angle calculation
        mcp_vector = m_V.to_vector(proj_mcp, proj_mcp_b)
        tar_vec = m_V.to_vector(np.array(proj_mcp), np.array(proj_pip))

        # thumb angle
        angle = m_V.angle_between(np.array(tar_vec), np.array(mcp_vector))
        data[1] = angle

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

        # circle around tangent
        for i in range(0, 4):
            circle = m_V.create_circle_around_vector(tangent, mcps[i], dists[i], 20, dirs[i])
            closest = m_V.get_closest_point(pips[i], circle)
            # angle between the closest point on circle to mcp and pip to mcp vectors
            mcp_pip = m_V.to_vector(mcps[i], pips[i])
            mcp_facing = m_V.to_vector(mcps[i], closest)
            angle = m_V.angle_between(np.array(mcp_pip), np.array(mcp_facing))
            data[self.fingers[i + 1][0]] = angle

        # angles = [int(degrees(d)) for d in data if d != 0]
        # print(angles)
        return data

    def get_nz_angles(self, hand):
        """ get approximate z angle
            by projecting mcp and dip on a plane based on the palm
            calculating the angle based on the mcps and dips """
        joints = np.array([[0, 1, 2]])
        data = [0] * 20
        plane_tris = [
            [1, 5],  # thumb
            [5, 9],  # index
            [9, 13],  # middle
            [13, 17],  # ring
            [17, 13]  # pinky -> [17, 13]
        ]

        # project proximal phalanges on plane based on surrounding metacarpals
        for idx, finger in enumerate(self.fingers):
            if idx != 0:
                # palm based plane
                plane = np.array([
                    np.array([0, 0, 0]),
                    hand[5][1],
                    hand[17][1]
                ])
            else:
                # thumb based plane
                plane = np.array([
                    np.array([0, 0, 0]),
                    hand[1][1],
                    hand[5][1]
                ])

            # PROJ MCP ON PLANE
            proj_mcp = m_V.project_vec_on_plane(
                plane, joints, hand[plane_tris[idx][0]][1])
            proj_mcp_b = m_V.project_vec_on_plane(
                plane, joints, hand[plane_tris[idx][1]][1])

            # PROJ PIP ON PLANE
            pip = hand[finger[0] + 1]
            proj_pip = m_V.project_vec_on_plane(
                plane, joints, np.array(pip[1])*2)

            if idx < 4:  # mcp "joint" as vector
                mcp_vector = m_V.to_vector(proj_mcp, proj_mcp_b)

            else:  # change vector direction
                mcp_vector = m_V.to_vector(proj_mcp_b, proj_mcp)

            # mcp to pip vec
            pip_vec = m_V.to_vector(np.array(proj_mcp), np.array(proj_pip))
            angle = m_V.angle_between(np.array(pip_vec), np.array(mcp_vector))

            if angle is None:
                break

            data[finger[0]] = angle # noqa

        return data

    def get_z_angles(self, hand):
        """ get approximate y angle
            by projecting the proximal phalanges on a plane
            taking the vector from wrist to knuckle
            and calculating the angle offset."""
        joints = np.array([[0, 1, 2]])
        data = [0] * 20
        plane_tris = [
            [1, 5],
            [5, 9],
            [9, 13],
            [13, 17],
            [13, 17]
        ]

        # project proximal phalanges on plane based on surrounding metacarpals
        for idx, finger in enumerate(self.fingers):
            mcp = hand[finger[0]][1]
            plane = np.array([
                np.array([0, 0, 0]),
                hand[plane_tris[idx][0]][1],
                hand[plane_tris[idx][1]][1]
            ])

            proj_mcp = m_V.project_vec_on_plane(
                plane,
                joints,
                np.array(mcp)
            )

            dip = hand[finger[0] + 1][1]
            proj_dip = m_V.project_vec_on_plane(
                plane,
                joints,
                np.array(dip)
            )

            angle = m_V.angle_between(np.array(proj_dip), np.array(proj_mcp))

            if angle is None:
                break

            data[finger[0]] = angle
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
