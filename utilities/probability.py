import numpy as np
from scipy import stats


def calculate_angle(pn_prime, p_hat):

    if pn_prime.shape[0] != 2:
        # remove z
        pn_prime = pn_prime[:2]

    if p_hat.shape[0] != 2:
        # remove z
        p_hat = p_hat[:2]

    pn_prime = np.squeeze(pn_prime)
    p_hat = np.squeeze(p_hat)

    pn_norm = np.linalg.norm(pn_prime)
    p_hat_norm = np.linalg.norm(p_hat)

    dot = np.dot(pn_prime, p_hat)

    cos_angle = dot / (pn_norm * p_hat_norm)

    # in degree
    #angle_degree = np.arccos(cos_angle) * (180.0 / np.pi)

    # in radiance
    angle_radian = np.arccos(cos_angle)

    #print("a",angle_degree)
    #print(dot)
    return angle_radian

def calculate_probability_angle(angle, sigma, mu=0):

    # calculate pdf vor angle
    P_x = stats.norm.pdf(angle, mu, sigma)
    print(f'probability for angle: {angle*(180/np.pi)} degree: {P_x}')

def normalize_probability(p_goals, p_goal):
    return p_goal/(max(1, sum(p_goals)))