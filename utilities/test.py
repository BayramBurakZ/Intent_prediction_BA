import numpy as np
import pandas as pd
'''
b1 ,c1, d1, e1 = a3[0], a2[0]-3*a3[0]*s, a1[0]-2*a2[0]*s+3*a3[0]*s**2, a0[0]-a1[0]*s+a2[0]*s**2-a3[0]*s**3
    b2, c2, d2, e2 = a3[1], a2[1]-3*a3[1]*s, a1[1]-2*a2[1]*s+3*a3[1]*s**2, a0[1]-a1[1]*s+a2[1]*s**2-a3[1]*s**3
    b3, c3, d3, e3 = a3[2], a2[2]-3*a3[2]*s, a1[2]-2*a2[2]*s+3*a3[2]*s**2, a0[2]-a1[2]*s+a2[2]*s**2-a3[2]*s**3
    
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
                 
                 
    """



