import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.ticker import FuncFormatter


def plot2d(x, y):
    # Plotting the points
    plt.plot(x, y, 'ro')
    plt.title('Sample Point Plot')
    plt.xlabel('x values')
    plt.ylabel('y values')

    # Show plot
    plt.show()


def plot_3d_line(df):
    fig = plt.figure()

    # 3D-Subplot
    ax = fig.add_subplot(111, projection='3d')

    # draw line between points
    ax.plot(df['x'], df['y'], df['z'], marker='o')

    ax.set_title('3D')
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')

    plt.show()


def draw_3d_curve(M1,M2,p, prime, pg1, pg2, num_points=100):
    """plots curves in 3D space from a cubic polynomial

    :param M1: Coefficient matrix
    :param num_points: step size
    """
    t = np.linspace(0, 1, num_points)

    # first polynomial
    x1 = M1[0, 0] * t ** 3 + M1[0, 1] * t ** 2 + M1[0, 2] * t + M1[0, 3]
    y1 = M1[1, 0] * t ** 3 + M1[1, 1] * t ** 2 + M1[1, 2] * t + M1[1, 3]
    z1 = M1[2, 0] * t ** 3 + M1[2, 1] * t ** 2 + M1[2, 2] * t + M1[2, 3]

    #second polynomial
    x2 = M2[0, 0] * t ** 3 + M2[0, 1] * t ** 2 + M2[0, 2] * t + M2[0, 3]
    y2 = M2[1, 0] * t ** 3 + M2[1, 1] * t ** 2 + M2[1, 2] * t + M2[1, 3]
    z2 = M2[2, 0] * t ** 3 + M2[2, 1] * t ** 2 + M2[2, 2] * t + M2[2, 3]

    #boundry conditions
    x1[0] = p[0]
    y1[0] = p[1]
    z1[0] = p[2]

    x2[0] = p[0]
    y2[0] = p[1]
    z2[0] = p[2]

    x1[-1] = pg1[0]
    y1[-1] = pg1[1]
    z1[-1] = pg1[2]

    x2[-1] = pg2[0]
    y2[-1] = pg2[1]
    z2[-1] = pg2[2]


    # plot 3d curve
    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    ax.plot(x1, y1, z1, label='PG_1') #first polynomial
    ax.plot(x2, y2, z2, label='PG_2') #second polynomial

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    plt.title('3D')
    ax.legend(loc='upper left')

    formatter = FuncFormatter(lambda x, pos: "{:.2f}".format(x))
    ax.xaxis.set_major_formatter(formatter)

    plt.show()
