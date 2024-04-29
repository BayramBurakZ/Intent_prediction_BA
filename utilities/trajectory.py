import numpy as np


def position_derivative(p, pn, p_t, pn_t):
    return (pn - p) / (pn_t - p_t)


def normalize(p):
    return p / np.linalg.norm(p)


def position_derivative_normalized(p, pn, p_t, pn_t):
    delta = p - pn
    distance = np.linalg.norm((delta) / (p_t - pn_t))
    return delta / distance


def calculate_path_coordinate(p, pn, pg):
    distance_a = np.linalg.norm(pn - p)
    distance_b = np.linalg.norm(pg - pn)
    return distance_a / (distance_a + distance_b)


def calculate_polynomial(M, s):
    x = np.polyval(M[0], s)
    y = np.polyval(M[1], s)
    z = np.polyval(M[2], s)

    return np.array([[x], [y], [z]])


def prediction_model_matrix(p, p_prime, pg, pg_prime=np.zeros(0)):
    if (pg_prime.any()):
        a0 = np.array(p, copy=True)
        a1 = p_prime
        a2 = 3 * pg - 3 * p - 2 * p_prime
        a3 = -2 * pg + 2 * p + p_prime
    else:
        a0 = np.array(p, copy=True)
        a1 = p_prime
        a2 = 1.5 * pg - 1.5 * p - 1.5 * p_prime
        a3 = -0.5 * pg + 0.5 * p + 0.5 * p_prime

    # coefficients of cubic polynom 3x4 matrix
    Mp = np.zeros((3, 4))
    for i in range(3):
        Mp[i] = [a3[i, 0], a2[i, 0], a1[i, 0], a0[i, 0]]

    # coefficients of first derivative cubic polynom 3x3 matrix
    Mv = np.zeros((3, 3))
    for i in range(3):
        Mv[i] = [3 * a3[i, 0], 2 * a2[i, 0], a1[i, 0]]

    '''
    # coefficients of second derivative cubic polynom 3x3 matrix
    Ma = np.zeros((3, 2))
    for i in range(3):
        Ma[i] = [6 * a3[i, 0], 2 * a2[i, 0]]
    '''

    return (Mp, Mv)
