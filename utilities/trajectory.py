import numpy as np


def position_derivative(p, pn, p_t, pn_t):
    """ calculates the approximated derivative of two points with respect to time

    :param p: measured point at t_n-1
    :param pn: measured point at t_n
    :param p_t: time t_n-1
    :param pn_t: time t_n
    :return: approximated derivative
    """
    return (pn - p) / (pn_t - p_t)


def normalize(p):
    """ normalizes a vector"""
    return p / np.linalg.norm(p)


def calculate_path_coordinate(p, pn, pg):
    """ calculates the predicted path coordinate along the prediction model trajectory

    :param p: measured point at t_n-1
    :param pn: measured point at t_n
    :param pg: position of goal
    :return: predicted path coordinate
    """
    distance_a = np.linalg.norm(pn - p)
    distance_b = np.linalg.norm(pg - pn)
    return distance_a / (distance_a + distance_b)


def calculate_polynomial(M, s):
    """ calculates the value of a polynomial at point s

    :param M: coefficient matrix
    :param s: value
    :return: value of a polynomial at point s
    """
    x = np.polyval(M[0], s)
    y = np.polyval(M[1], s)
    z = np.polyval(M[2], s)

    return np.array([[x], [y], [z]])


def prediction_model_matrix(p, p_prime, pg, pg_prime=np.zeros(0)):
    """ calculates the coefficients of the trajectory model and it's derivative

    :param p: measured point at t_n-1
    :param p_prime: derivative of p
    :param pg: position of goal
    :param pg_prime: position of goal derivative (used if affordance of a goal applies)
    :return: coefficient matrix of the trajectory model, and it's derivative as a tuple
    """
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
