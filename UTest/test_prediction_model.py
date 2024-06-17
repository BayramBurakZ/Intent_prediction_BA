import unittest

import numpy as np

from prediction_model import calc_angle


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


if __name__ == '__main__':
    unittest.main()
