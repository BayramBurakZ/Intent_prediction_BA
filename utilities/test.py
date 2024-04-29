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
                 
                 
                 
                 def draw_3d_curve(M1,M2,p, pn, pg1, pg2, pn_prime, num_points=100):
    """plots curves in 3D space from a cubic polynomial

    :param M1: Coefficient matrix
    :param num_points: step size
    """
    t = np.linspace(0, 1, num_points)

    """
    # first polynomial
    x1 = M1[0, 0] * t ** 3 + M1[0, 1] * t ** 2 + M1[0, 2] * t + M1[0, 3]
    y1 = M1[1, 0] * t ** 3 + M1[1, 1] * t ** 2 + M1[1, 2] * t + M1[1, 3]
    z1 = M1[2, 0] * t ** 3 + M1[2, 1] * t ** 2 + M1[2, 2] * t + M1[2, 3]

    #second polynomial
    x2 = M2[0, 0] * t ** 3 + M2[0, 1] * t ** 2 + M2[0, 2] * t + M2[0, 3]
    y2 = M2[1, 0] * t ** 3 + M2[1, 1] * t ** 2 + M2[1, 2] * t + M2[1, 3]
    z2 = M2[2, 0] * t ** 3 + M2[2, 1] * t ** 2 + M2[2, 2] * t + M2[2, 3]
    """
    M1[0,0] = -10
    x1 = -2*t**3+6*t**2+2.4*t+4.25
    y1 = -2.39*t**3+7.17*t**2+3.37*t-2.49
    z1 = 3.38*t**3-t**2+2.3*t+2.25
    """
    x1 = np.polyval(M1[0], t)
    y1 = np.polyval(M1[1], t)
    z1 = np.polyval(M1[2], t)
    """
    x2 = np.polyval(M2[0], t)
    y2 = np.polyval(M2[1], t)
    z2 = np.polyval(M2[2], t)

    print(p)
    #boundry conditions
    x1[0] = p[0,0]
    y1[0] = p[1,0]
    z1[0] = p[2,0]

    x2[0] = p[0,0]
    y2[0] = p[1,0]
    z2[0] = p[2,0]

    #x1[-1] = pg1[0,0]
    #y1[-1] = pg1[1,0]
    #z1[-1] = pg1[2,0]

    x2[-1] = pg2[0,0]
    y2[-1] = pg2[1,0]
    z2[-1] = pg2[2,0]
    # plot 3d curve
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')
    ax.plot(x1, y1, z1, label='PG_1') #first polynomial
    ax.plot(x2, y2, z2, label='PG_2', color = 'yellow') #second polynomial

    #points
    ax.scatter(p[0,0], p[1,0], p[2,0],label='p' ,color='red')
    ax.scatter(pn[0, 0], pn[1, 0], pn[2, 0],label='pn', color='yellow')
    ax.scatter(pg1[0, 0], pg1[1, 0], pg1[2, 0], label='pg1', color='green')
    ax.scatter(pg2[0, 0], pg2[1, 0], pg2[2, 0],label='pg2', color='blue')

    #tangent
    ax.quiver(pn[0, 0], pn[1, 0], pn[2, 0],pn_prime[0, 0], pn_prime[1, 0], pn_prime[2, 0], color='red', length=0.05, normalize=True)

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    plt.title('3D')
    ax.legend(loc='upper left')

    #formatter = FuncFormatter(lambda x, pos: "{:.2f}".format(x))
    #ax.xaxis.set_major_formatter(formatter)

    plt.show()
number = 9
pathr = r'..\trajectories\right_hand\right_'
pathr += str(number) + '.csv'

dfr = pd.read_csv(pathr)

dfr['x'] = dfr['x'].apply(lambda x: x*3)
dfr['y'] = dfr['y'].apply(lambda x: x*3)
dfr['z'] = dfr['z'].apply(lambda x: x*3)

dfr.to_csv(r'..\trajectories\chosen_trajectories\testr.csv', index=False)

-2t^{3}+6t^{2}+2.4t+4.25,-2.39t^{3}+7.17t^{2}+3.37t-2.49,3.38t^{3}-1t^{2}+2.3t+2.25


 # plot cubic polynomial
    for x in M:
        print(x[0][1])
        x = np.polyval(x[0][0], t)
        y = np.polyval(x[0][1], t)
        z = np.polyval(x[0][2], t)

        ax.plot(x, y, z, label='parametric curve')
'''


import matplotlib.pyplot as plt
import numpy as np

def berechne_tangentenvektor(punkt1, zeit1, punkt2, zeit2):
    # Umwandlung der Punkte in numpy arrays für einfache Berechnungen
    punkt1 = np.array(punkt1)
    punkt2 = np.array(punkt2)

    # Berechnung der Differenz zwischen den Punkten und den Zeitstempeln
    delta_punkt = punkt2 - punkt1
    delta_zeit = zeit2 - zeit1

    # Berechnung des Tangentenvektors
    tangentenvektor = delta_punkt / delta_zeit

    return tangentenvektor

# Test des Codes
punkt1 = [1, 2, 3]
zeit1 = 1
punkt2 = [4, 5, 6]
zeit2 = 2

tangentenvektor = berechne_tangentenvektor(punkt1, zeit1, punkt2, zeit2)
print("Der Tangentenvektor ist:", tangentenvektor)



