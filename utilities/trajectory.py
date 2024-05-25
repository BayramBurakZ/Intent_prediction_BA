import numpy as np


def position_derivative(p1, p2, t1, t2):
    """ calculates the approximated normalized direction of two points with respect to time """
    d = (p2 - p1) / (t2 - t1)
    return d / np.linalg.norm(d)



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
    # TODO: some new points don't translate well (consider the case of backwards motion!)
    distance_a = np.linalg.norm(pn - p)
    distance_b = np.linalg.norm(pg - pn)
    return distance_a / (distance_a + distance_b)


def calculate_polynomial(m, s):
    """ calculates the value of a polynomial at point s """
    x = np.polyval(m[0], s)
    y = np.polyval(m[1], s)
    z = np.polyval(m[2], s)

    return np.array([[x], [y], [z]])


def prediction_model_matrix(p, p_prime, pg):
    """ calculates the coefficients of the trajectory model and it's derivative

    :param p: measured point at t_n-1
    :param p_prime: derivative of p
    :param pg: position of goal
    :return: coefficient matrix of the trajectory model, and it's derivative as a tuple
    """

    a0 = np.array(p, copy=True)
    a1 = p_prime
    a2 = 1.5 * pg - 1.5 * p - 1.5 * p_prime
    a3 = -0.5 * pg + 0.5 * p + 0.5 * p_prime

    # coefficients of cubic polynom 3x4 matrix
    mp = np.zeros((3, 4))
    for i in range(3):
        mp[i] = [a3[i, 0], a2[i, 0], a1[i, 0], a0[i, 0]]

    # coefficients of first derivative cubic polynom 3x3 matrix
    mv = np.zeros((3, 3))
    for i in range(3):
        mv[i] = [3 * a3[i, 0], 2 * a2[i, 0], a1[i, 0]]

    '''
    # coefficients of second derivative cubic polynom 3x3 matrix
    Ma = np.zeros((3, 2))
    for i in range(3):
        Ma[i] = [6 * a3[i, 0], 2 * a2[i, 0]]
    '''
    return mp, mv
