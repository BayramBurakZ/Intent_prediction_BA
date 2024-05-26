from unittest import TestCase
from probability_evaluator import calculate_angle

import numpy as np


class TestProbabilityEvaluator(TestCase):
    def test_evaluate_angles(self):
        a1 = np.array([[1], [0], [1]])
        a2 = np.array([[1], [0], [1]])
        a3 = np.array([[0], [1], [1]])
        a4 = np.array([[1], [1], [1]])
        a5 = np.array([[1], [1], [1]])

        b1 = np.array([[0], [1], [1]])
        b2 = np.array([[1], [0], [1]])
        b3 = np.array([[0], [-1], [1]])
        b4 = np.array([[-1], [-1], [1]])
        b5 = np.array([[1], [-1], [1]])

        c1 = np.pi / 2
        c2 = 0
        c3 = np.pi
        c4 = np.pi
        c5 = np.pi / 2

        vector_a = [a1, a2, a3, a4, a5]
        vector_b = [b1, b2, b3, b4, b5]
        vector_c = [c1, c2, c3, c4, c5]

        for i in range(len(vector_a)):
            self.assertAlmostEqual(calculate_angle(vector_a[i], vector_b[i]), vector_c[i], 5)
