import numpy as np


def position_velocity(pp, pn):
    delta_pn = pn - pp
    delta_t = delta_pn[0]
    delta_pn = np.delete(delta_pn, 0, 0)

    return delta_pn / delta_t


def prediction_model_matrix(s, p, p_prime, pg, pg_prime=np.zeros(0)):
    """Returns coefficient matrix for model prediction model and its derivation

    :param s: normalized path coordinate of p
    :param p: last observed wrist position
    :param p_prime: derivative of wrist position along the path
    :param pg: goal position
    :param pg_prime: derivative of goal position along the path

    :return: coefficient matrix
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
        Mp[i] = [a3[i, 0],
                 a2[i, 0] - 3 * a3[i, 0] * s,
                 a1[i, 0] - 2 * a2[i, 0] * s + 3 * a3[i, 0] * s ** 2,
                 a0[i, 0] - a1[i, 0] * s + a2[i, 0] * s ** 2 - a3[i, 0] * s ** 3]

    # coefficients of first derivative cubic polynom 3x3 matrix
    Mv = np.zeros((3, 3))
    for i in range(3):
        Mv[i] = [3 * a3[i, 0],
                 2 * (a2[i, 0] - 3 * a3[i, 0] * s),
                 a1[i, 0] - 2 * a2[i, 0] * s + 3 * a3[i, 0] * s ** 2]

    # coefficients of second derivative cubic polynom 3x3 matrix
    Ma = np.zeros((3, 2))
    for i in range(3):
        Mv[i] = [6 * a3[i, 0],
                 2 * (a2[i, 0] - 3 * a3[i, 0] * s)]

    return (Mp, Mv, Ma)
