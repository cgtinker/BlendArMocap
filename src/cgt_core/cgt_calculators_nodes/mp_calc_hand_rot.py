import numpy as np
from . import calc_utils, cgt_math
from ..cgt_patterns import cgt_nodes


class HandRotationCalculator(cgt_nodes.CalculatorNode, calc_utils.ProcessorUtils):
    fingers = [
        [1, 5],  # thumb
        [5, 9],  # index finger
        [9, 13],  # middle finger
        [13, 17],  # ring finger
        [17, 21],  # pinky
    ]

    data: np.ndarray = None

    left_hand_data: np.ndarray = None
    right_hand_data: np.ndarray = None

    left_angles: list = None
    right_angles: list = None

    left_scale: np.ndarray = None
    right_scale: np.ndarray = None

    def init_data(self):
        """ Process and map received data from mediapipe before key-framing. """
        self.left_hand_data = self.set_global_origin(self.data[0])
        self.right_hand_data = self.set_global_origin(self.data[1])

        # get finger angles
        self.left_angles = self.finger_angles(self.left_hand_data)
        self.right_angles = self.finger_angles(self.right_hand_data)

        # get hand rotation
        left_hand_rot = self.global_hand_rotation(self.left_hand_data, 0, "L")
        if left_hand_rot is not None:
            self.left_angles.append(left_hand_rot)
        right_hand_rot = self.global_hand_rotation(self.right_hand_data, 100, "R")  # offset for euler combat
        if right_hand_rot is not None:
            self.right_angles.append(right_hand_rot)

    def update(self, data, frame=-1):
        """ Returns processing results or empty lists. """
        locations = [[], []]
        angles = [[], []]

        self.data = data
        self.init_data()
        if self.right_hand_data is not None:
            if not self.has_duplicated_results(self.right_hand_data, "hand", 0):
                locations[1] = self.right_hand_data
                angles[1] = self.right_angles

        if self.left_hand_data is not None:
            if not self.has_duplicated_results(self.left_hand_data, "hand", 1):
                locations[0] = self.left_hand_data
                angles[0] = self.left_angles

        return [locations, angles, [[], []]], frame

    def finger_angles(self, hand):
        """ Get finger x-angles from landmarks. """
        if not hand or len(hand) < 20:
            return []

        x_angles = self.get_x_angles(hand)
        z_angles = self.get_z_angles(hand)

        data = []
        for idx in range(0, 20):
            if x_angles[idx] != 0 or z_angles[idx] != 0:
                joint_angle = [idx, np.array([x_angles[idx], 0, z_angles[idx]])]
                data.append(joint_angle)

        return data

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
            thumb_proj = [cgt_math.project_vec_on_plane(plane, joints, p)
                          for p in [hand[1][1], hand[5][1], hand[2][1]]]

            # vectors to calculate angle
            thumb_vecs = [cgt_math.to_vector(tp[0], tp[1]) for tp in [
                [thumb_proj[0], thumb_proj[1]],
                [thumb_proj[0], thumb_proj[2]]]]

            return cgt_math.angle_between(np.array(thumb_vecs[0]), np.array(thumb_vecs[1]))

        data[1] = calculate_thumb_angle()

        # calculate other finger angles
        tangent = cgt_math.to_vector(np.array(hand[5][1]), np.array(hand[17][1]))
        # get pips, mcps and their dists (mcps projected on tangent)
        mcps = [cgt_math.project_point_on_vector(
            np.array(hand[finger[0]][1]), np.array(hand[5][1]), np.array(hand[17][1]))
            for finger in self.fingers[1:]]
        pips = [np.array(hand[finger[1] - 2][1]) for finger in self.fingers[1:]]
        dists = [cgt_math.get_vector_distance(mcps[i], pips[i]) for i in range(0, 4)]

        # circle direction vectors related to the hand to calc angles
        pinky_vec = cgt_math.to_vector(np.array(hand[0][1]), np.array(hand[17][1]))
        thumb_vec = cgt_math.to_vector(np.array(hand[1][1]), np.array(hand[5][1]))
        dirs = [pinky_vec, pinky_vec, thumb_vec, thumb_vec]

        points = 20
        for i in range(0, 4):
            # create a circle around tangent in target dir
            # and find the closest point from circle to pip
            circle = cgt_math.create_circle_around_vector(tangent, mcps[i], dists[i], points, dirs[i])
            closest = cgt_math.get_closest_idx(pips[i], circle)

            # angle between the closest point on circle to mcp and pip to mcp vectors
            mcp_pip = cgt_math.to_vector(mcps[i], pips[i])
            mcp_closest = cgt_math.to_vector(mcps[i], circle[closest])

            # expand the arr of the circle to avoid index errors
            # form a triangle on the circle facing the closet point to the pip
            expanded_circle = circle + circle + circle
            a = expanded_circle[closest + points + 6]
            b = expanded_circle[closest + points - 6]

            # calculate the normal from the triangle
            plane = np.array([a, circle[closest], b])
            normal = cgt_math.normal_from_plane(plane)
            normal = cgt_math.normalize(normal)

            # get the distance from the triangle to the pip
            dist = cgt_math.distance_from_plane(pips[i], normal, circle[closest])

            # check if the finger angle should be pos or neg based on the dist
            angle = cgt_math.angle_between(np.array(mcp_pip), np.array(mcp_closest))
            if dist < 0:
                angle = -angle
            else:
                pass

            data[self.fingers[i + 1][0]] = angle

        return data

    def get_x_angles(self, hand):
        """ Get finger x angle by calculating the angle between each finger joint """
        # add the wrist as origin to all fingers (0, 0, 0)
        fingers = [[hand[idx][1] for idx in range(finger[0], finger[1])] for finger in self.fingers]
        wrist_origin = np.array([0, 0, 0])
        fingers = [np.array([wrist_origin] + finger) for finger in fingers]
        joints = np.array([[0, 1, 2]])

        # straighten fingers by plane projection
        for idx, finger in enumerate(fingers):
            plane = np.array([np.array([0, 0, 0]), finger[1], finger[4]])
            f = [cgt_math.project_vec_on_plane(plane, joints, p) for p in finger]
            fingers[idx] = f

        # setup joints to calc finger angles
        x_joints = [[0, 1, 2], [1, 2, 3], [2, 3, 4]]
        x_finger_angles = [cgt_math.joint_angles(finger, x_joints) for finger in fingers]

        data = [0] * 20
        for idx, angles in enumerate(x_finger_angles):
            if angles is None:
                break

            # iter over every finger joint and calc angle
            mcp, tip = self.fingers[idx]
            for angle_idx, finger_idx in enumerate(range(mcp, tip - 1)):
                data[finger_idx] = angles[angle_idx]

        return data

    def global_hand_rotation(self, hand, combat_idx_offset: int = 0, orientation: str = "R"):
        """ Calculates approximate hand rotation by generating
            a matrix using the palm as approximate triangle. """
        if hand == []:
            return []

        # default hand rotation for a rigify A-Pose rig,
        if orientation == "R":
            rotation = [-60, 60, 0]
        else:
            rotation = [-60, -60, 0]

        # rotate points before calculating the rotation
        rotated_points = [cgt_math.rotate_point_euler(np.array(hand[idx][1]), rotation) for idx in [1, 5, 13]]

        # setup vectors to create an matrix
        tangent = cgt_math.normalize(cgt_math.to_vector(
            rotated_points[0],
            rotated_points[1]
        ))
        binormal = cgt_math.normalize(cgt_math.to_vector(
            rotated_points[1],
            rotated_points[2]
        ))
        normal = cgt_math.normalize(np.cross(binormal, tangent))

        # rotation from matrix
        try:
            matrix = cgt_math.generate_matrix(normal, tangent, binormal)
            loc, quart, sca = cgt_math.decompose_matrix(matrix)
            euler = self.try_get_euler(quart, prev_rot_idx=combat_idx_offset)
            hand_rotation = ([0, euler])
        except TypeError:
            # TODO: reactivate
            # logging.warning("Mathutils are only support in Blender, switch decomposition tag")
            hand_rotation = ()

        return hand_rotation

    def landmarks_to_hands(self, left_hand, right_hand):
        """ Determines to which hand the landmark data belongs """
        left_hand = self.set_global_origin(left_hand)
        right_hand = self.set_global_origin(right_hand)
        return left_hand, right_hand

    @staticmethod
    def set_global_origin(data):
        """ Sets the wrist to (0, 0, 0) while the wrist is the origin of the fingers.
            Changes the x-y-z order to match blenders coordinate system. """
        if data is None or len(data) == 0:
            return data

        if len(data) > 0:
            data = [[idx, np.array([-landmark[0], landmark[2], -landmark[1]])] for idx, landmark in data[0]]
            data = [[idx, landmark - data[0][1]] for idx, landmark in data]

        return data
