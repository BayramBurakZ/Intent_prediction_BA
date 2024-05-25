import numpy as np
from scipy import stats
from numpy.typing import NDArray
from typing import List


class ProbabilityEvaluator:
    def __init__(self, number_of_goals):
        self.number_of_goals = number_of_goals
        self.sample_size_of_goals = [0] * number_of_goals
        self.probability_goals = [0] * number_of_goals

    def evaluate_angles(self, dp_current, direction_vectors: List[NDArray[np.float64]]):

        angles = []
        for dv in direction_vectors:
            angles.append(calculate_angle(dp_current, dv))

        sd_of_angles = calculate_standard_deviation(angles)

        for i in range(self.number_of_goals):
            probability_angle = calculate_probability_angle(angles[i], sd_of_angles)
            self.probability_goals[i] = calculate_probability_goal(self.probability_goals[i], probability_angle)

            if self.probability_goals[i] == 0:
                self.sample_size_of_goals[i] = 0
            else:
                self.sample_size_of_goals[i] += 1

        norm_divisor = probability_normalization_divisor(self.probability_goals)
        self.probability_goals = [x / norm_divisor for x in self.probability_goals]


def calculate_angle(v1, v2):
    """ calculates the angle on x,y plane between two vectors """
    if v1.shape[0] != 2:
        # remove z
        v1 = v1[:2]

    if v2.shape[0] != 2:
        # remove z
        v2 = v2[:2]

    v1 = np.squeeze(v1)
    v2 = np.squeeze(v2)

    # normalize
    v1_norm = np.linalg.norm(v1)
    v2_norm = np.linalg.norm(v2)

    # calculate angle
    dot = np.dot(v1, v2)
    cos_angle = dot / (v1_norm * v2_norm)

    return np.arccos(cos_angle)  # in radiance


def calculate_standard_deviation(angles):
    sigma = np.std(angles)

    # boundaries for standard deviation
    min_sd = np.sqrt(1 / 8)
    max_sd = np.sqrt(1 / 16)

    if (sigma < min_sd):
        sigma = min_sd

    if (sigma > max_sd):
        sigma = max_sd

    return sigma


def calculate_probability_angle(angle, sigma, mu=0):
    return stats.norm.pdf(angle, mu, sigma)


def calculate_probability_goal(cumulative_probability, angle_probability):
    min_probability = 0.01

    if (angle_probability < min_probability):
        return 0

    if (cumulative_probability < min_probability):
        return angle_probability
    else:
        return cumulative_probability * angle_probability


def probability_normalization_divisor(probability_all_goals):
    return max(1, sum(probability_all_goals))


