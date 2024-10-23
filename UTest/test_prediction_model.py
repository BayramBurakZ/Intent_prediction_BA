import unittest
import numpy as np
from prediction_model import calc_angle, calc_hand_towards_goal


class TestCalcAngle(unittest.TestCase):

    def setUp(self):
        self.vector_a = [
            np.array([1, 0, 1]),
            np.array([1, 0, 1]),
            np.array([0, 1, 1]),
            np.array([1, 1, 1]),
            np.array([1, 1, 1]),
            np.array([1, 0, 0]),
            np.array([2, 3, 4]),
            np.array([3, 5, -1]),
        ]
        self.vector_b = [
            np.array([0, 1, 1]),
            np.array([1, 0, 1]),
            np.array([0, -1, 1]),
            np.array([-1, -1, 1]),
            np.array([1, -1, 1]),
            np.array([-1, 0, 0]),
            np.array([1, -2, 1]),
            np.array([-3, 2, 0]),
        ]
        self.vector_c = [
            np.pi / 2,  # 90 degrees
            0,  # 0 degrees
            np.pi,  # 180 degrees
            np.pi,  # 180 degrees
            np.pi / 2,  # 90 degrees
            np.pi,  # 180 degrees
            2.08994244104142,  # 119.744881296942224 degrees
            1.523213223517913  # 87.273689006093735 degrees
        ]

    def test_calc_angle(self):
        for i in range(len(self.vector_a)):
            with self.subTest(i=i):
                calculated_angle = calc_angle(self.vector_a[i], self.vector_b[i])
                print(f"Test case {i}: Expected angle {self.vector_c[i]}, Calculated angle {calculated_angle}")
                self.assertAlmostEqual(calculated_angle, self.vector_c[i], places=5)


class TestCalcHandTowardsGoal(unittest.TestCase):

    def setUp(self):
        self.goals = {
            1: np.array([0.6, -0.4, 0.03]),
            3: np.array([0.4, -0.2, 0.03]),
            5: np.array([0.4, 0.2, 0.03]),
            7: np.array([0.6, 0.4, 0.03])
        }
        self.hand_position = np.array([0.6, 0, 0.03])

    def test_direction_x(self):
        direction = np.array([0.01, 0, 0])  # Direction towards +x
        expected_results = {1: False, 3: False, 5: False, 7: False}
        for goal_id, expected in expected_results.items():
            with self.subTest(goal_id=goal_id):
                result = calc_hand_towards_goal(self.goals[goal_id], self.hand_position, direction)
                self.assertEqual(result, expected)

    def test_direction_minus_x(self):
        direction = np.array([-0.01, 0, 0])  # Direction towards -x
        expected_results = {1: False, 3: True, 5: True, 7: False}
        for goal_id, expected in expected_results.items():
            with self.subTest(goal_id=goal_id):
                result = calc_hand_towards_goal(self.goals[goal_id], self.hand_position, direction)
                self.assertEqual(result, expected)

    def test_direction_y(self):
        direction = np.array([0, 0.01, 0])  # Direction towards +y
        expected_results = {1: False, 3: False, 5: True, 7: True}
        for goal_id, expected in expected_results.items():
            with self.subTest(goal_id=goal_id):
                result = calc_hand_towards_goal(self.goals[goal_id], self.hand_position, direction)
                self.assertEqual(result, expected)

    def test_direction_minus_y(self):
        direction = np.array([0, -0.01, 0])  # Direction towards -y
        expected_results = {1: True, 3: True, 5: False, 7: False}
        for goal_id, expected in expected_results.items():
            with self.subTest(goal_id=goal_id):
                result = calc_hand_towards_goal(self.goals[goal_id], self.hand_position, direction)
                self.assertEqual(result, expected)


if __name__ == '__main__':
    unittest.main()
