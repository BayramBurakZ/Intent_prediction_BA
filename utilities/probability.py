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

    v1_norm = np.linalg.norm(v1)
    v2_norm = np.linalg.norm(v2)

    dot = np.dot(v1, v2)

    cos_angle = dot / (v1_norm * v2_norm)

    return np.arccos(cos_angle)  # in radiance


def calculate_probability_angle(angle, sigma, mu=0):
    p_x = stats.norm.pdf(angle, mu, sigma)
    print(f'probability for angle: {angle * (180 / np.pi)} degree: {p_x}')


def normalize_probability(all_goals, goal):
    return goal / (max(1, sum(all_goals)))
