import numpy as np
from scipy import stats


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


def calculate_variance(angles):
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
    p_x = stats.norm.pdf(angle, mu, sigma)
    # print(f'probability for angle: {angle * (180 / np.pi)} degree: {p_x}')


def calculate_probability_goal(cumulative_probability, angle_probability, norm_divisor):
    min_probability = 0.001

    if(angle_probability < min_probability):
        return 0

    if(cumulative_probability < min_probability):
        return angle_probability / norm_divisor
    else:
        return cumulative_probability * angle_probability / norm_divisor

def probability_normalization_divisor(probability_all_goals):
    return max(1, sum(probability_all_goals))
