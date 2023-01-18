from ..cgt_core.cgt_calculators_nodes.cgt_math import *
import unittest
import math


class TestMathutils(unittest.TestCase):
    vertices = np.array(
        [[-1, -1, -1], [1, -1, -1], [1, 1, -1], [-1, 1, -1],
         [-1, -1, 1], [1, -1, 1], [1, 1, 1], [-1, 1, 1]]
    )
    faces = np.array(
        [[0, 3, 1], [1, 3, 2], [2, 3, 0],
         [0, 1, 2], [4, 7, 5], [5, 7, 6],
         [6, 7, 4], [4, 5, 6], [0, 4, 3],
         [3, 4, 7], [1, 2, 5], [2, 6, 5],
         [0, 2, 1], [0, 6, 2], [3, 7, 6],
         [0, 3, 6], [4, 1, 5], [1, 2, 5]]
    )
    vec = np.array([0, 0.5, -15])

    def test_vector_length(self):
        self.assertAlmostEqual(vector_length(np.array([1, 2, 3])), 3.7416573867739413)
        self.assertAlmostEqual(vector_length(np.array([-1, -2, -3])), 3.7416573867739413)
        self.assertAlmostEqual(vector_length(np.array([0, 0, 0])), 0)
        self.assertAlmostEqual(vector_length(np.array([1, -2, 3])), 3.7416573867739413)

    def test_to_vector(self):
        self.lists_equals(to_vector(np.array([1, 2, 3]), np.array([4, 5, 6])), np.array([3, 3, 3]))
        self.lists_equals(to_vector(np.array([-1, -2, -3]), np.array([-4, -5, -6])), np.array([-3, -3, -3]))
        self.lists_equals(to_vector(np.array([1, -2, 3]), np.array([-4, 5, -6])), np.array([-5, 7, -9]))

    def test_normalize(self):
        self.lists_almost_equals(normalize(np.array([1, 2, 3])), np.array([0.26726124, 0.53452248, 0.80178373]))
        self.lists_almost_equals(normalize(np.array([-1, -2, -3])), np.array([-0.26726124, -0.53452248, -0.80178373]))

    def test_vector_length_2d(self):
        self.assertEqual(vector_length_2d(np.array([1, 1, 1]), np.array([1, 1, 1])), 0)
        self.assertEqual(round(vector_length_2d(np.array([1, 1, 1]), np.array([4, 5, 5])), 3), 6.403)
        self.assertEqual(round(vector_length_2d(np.array([0, 0, 0]), np.array([0, 1, 0]), del_axis="x"), 3), 1)

    def test_remove_axis(self):
        vectors = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
        args = ['X', 'Y', 'Z']
        expected = [
            [[2, 3], [5, 6], [8, 9]],
            [[1, 3], [4, 6], [7, 9]],
            [[1, 2], [4, 5], [7, 8]],
        ]
        for arr, axis in zip(expected, args):
            res = remove_axis(vectors, axis)
            for exp, r in zip(arr, res):
                self.lists_equals(exp, *r)

    def test_vector_distance(self):
        v1 = np.array([1, 2, 3])
        v2 = np.array([4, 5, 6])
        expected = math.sqrt(
            (v2[0] - v1[0]) ** 2 +
            (v2[1] - v1[1]) ** 2 +
            (v2[2] - v1[2]) ** 2
        )
        result = get_vector_distance(v1, v2)
        self.assertEqual(expected, result)

    def test_project_vec_on_vec(self):
        target = np.array([1, 1, 0])
        destination = np.array([0, 3, 5])
        expected_proj = np.array([1.5, 1.5, 0])
        actual_proj = project_vec_on_vec(target, destination)
        self.assertTrue(np.allclose(expected_proj, actual_proj))

    def test_angle_between(self):
        v1 = np.array([1, 0, 0])
        v2 = np.array([0, 1, 0])
        self.assertEqual(angle_between(v1, v2), np.pi / 2)

    # TODO: Check rotation (blendspace)
    # def test__rotate_towards(self):
    #     eye = np.array((0, 0, 0))
    #     target = np.array((0, 0, 1))
    #     print(m_rotate_towards(eye, target))
    #     print(np.eye(3))
    #     self.assertTrue(np.allclose(m_rotate_towards(eye, target), np.eye(3)))

    def test_create_normal_array(self):
        lam, norm = create_normal_array(self.vertices, self.faces)
        self.assertEqual(norm.all(), np.zeros((8, 3)).all())
        self.assertEqual(lam.shape, (18, 3))

    def test_project_vec_from_normal(self):
        n = np.array([1, 0, 0])
        v = np.array([4, 4, 4])
        self.assertEqual(project_vec_from_normal(n, v).all(), np.array([4, 0, 0]).all())

    def test_project_vec_on_plane(self):
        lam, norm = create_normal_array(self.vertices, self.faces)
        v = np.array([0, 0.5, -14])
        self.assertEqual(project_vec_on_plane(self.vertices, self.faces, v).all(), np.array([0, 0.5, 0]).all())

    def test_joint_angle(self):
        j1 = [np.array([0, 0]), np.array([1, 1])]
        j2 = [np.array([0, 1]), np.array([1, 1])]
        res = joint_angle(np.array([j1, j2, j1, j2]), [0, 1, 2])
        self.assertAlmostEqual(res[0][0], 1.570796326)

    def test_intersection_2d_vectors(self):
        origin_p1 = np.array([1, 2, 3])
        target_p1 = np.array([4, 5, 6])
        origin_p2 = np.array([7, 3, 9])
        target_p2 = np.array([10, 11, 12])
        del_axis = "Z"
        expected_output = np.array([10., 11.])
        output = intersection_2d_vectors(origin_p1, target_p1, origin_p2, target_p2, del_axis)
        self.lists_almost_equals(expected_output, output)

    def test_create_circle_around_vector(self):
        vector = np.array([1, 1, 0])
        center = np.array([0, 0, 0])
        radius = 1
        points = 5
        normal = np.array([0, 0, 1])
        circle = create_circle_around_vector(vector, center, radius, points, normal)
        self.lists_almost_equals([[0.0, 0.0, 1.0], [0.7071067811865475, -0.7071067811865475, 6.123233995736766e-17],
                                  [8.659560562354932e-17, -8.659560562354932e-17, -1.0],
                                  [-0.7071067811865475, 0.7071067811865475, -1.8369701987210297e-16],
                                  [-1.7319121124709863e-16, 1.7319121124709863e-16, 1.0]], circle)

    def test_circle_along_UV(self):
        expected = [[0.0, 1.0, 0.0], [0.0, 0.7071067811865476, 0.7071067811865475], [0.0, 6.123233995736766e-17, 1.0],
                    [0.0, -0.7071067811865475, 0.7071067811865476], [0.0, -1.0, 1.2246467991473532e-16],
                    [0.0, -0.7071067811865477, -0.7071067811865475], [0.0, -1.8369701987210297e-16, -1.0],
                    [0.0, 0.7071067811865475, -0.7071067811865477], [0.0, 1.0, -2.4492935982947064e-16]]
        result = circle_along_UV(center=np.array([0, 0, 0]), U=np.array([0, 1, 0]), V=np.array([0, 0, 1]), r=1,
                                 points=9)
        for res, exp in zip(result, expected):
            self.lists_almost_equals(res, exp)

        expected = np.array([[1.4082482904638631, 1.8164965809277263, 1.4082482904638631],
                             [1.8556218441086538, 1.388368032685012, 1.66663960760404],
                             [1.8017837257372733, 0.7327387580875756, 1.5345224838248488],
                             [1.278271574919028, 0.23366749430576053, 1.0892893384144144],
                             [0.591751709536137, 0.18350341907227383, 0.591751709536137],
                             [0.14437815589134617, 0.6116319673149877, 0.3333603923959598],
                             [0.1982162742627267, 1.2672612419124243, 0.4654775161751511],
                             [0.7217284250809719, 1.7663325056942394, 0.9107106615855856],
                             [1.408248290463863, 1.8164965809277263, 1.408248290463863]])
        result = np.array(
            circle_along_UV(center=np.array([1, 1, 1]), U=np.array([1, 2, 1]), V=np.array([3, -1, 2]), r=1,
                            points=9))
        self.assertEqual(result.all(), expected.all())

    def test_rotate_point_euler(self):
        point = np.array([10, 10, 10])
        euler = [90, 0, 0]
        origin = np.array([0, 0, 0])

        new_point = rotate_point_euler(point, euler, origin)
        assert np.allclose(new_point, np.array([10, 10, -10]))

    def test_rotate_point(self):
        point = [1, 2, 3]
        axis = [0, 0, 1]
        angle = 45
        result = rotate_point(point, axis, angle)
        expected_result = [-0.7071067811865477, 2.1213203435596424, 3.0]
        self.lists_almost_equals(expected_result, result)

    def test_distance_from_plane(self):
        self.assertEqual(distance_from_plane(np.array([1, 5, 2]), np.array([3, 0, -2]), np.array([2, 5, 1])), -5)
        self.assertEqual(distance_from_plane(np.array([1, 5, 2]), np.array([-3, 0, 2]), np.array([2, 5, 1])), 5)

    def test_normal_from_plane(self):
        expected = np.array([0, 0, 1])
        plane = np.array([[0, 0, 0], [1, 0, 0], [0, 1, 0]])
        res = normal_from_plane(plane)
        self.assertEqual(expected.all(), res.all())

    def test_matrix3x3_2quat(self):
        m = np.matrix([[1, 0, 0], [0, 1, 0], [0, 0, 1]])
        q = [-1, 0, 0, 0]
        self.assertEqual(matrix3x3_to_quaternion(m), q)

    def lists_almost_equals(self, l1, l2):
        for a, b in zip(l1, l2):
            self.assertAlmostEqual(a, b)

    def lists_equals(self, l1, l2):
        for a, b in zip(l1, l2):
            self.assertEqual(a, b)


if __name__ == '__main__':
    unittest.main()
