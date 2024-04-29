import numpy as np
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

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


def draw_3d_curve(M, p, pn, pn_prime, goals, path_points, tangential_vectors):

    ax = plt.figure().add_subplot(projection='3d')
    t = np.linspace(0, 1, 100)

    # plot cubic polynomial
    for m in M:
        x = np.polyval(m[0], t)
        y = np.polyval(m[1], t)
        z = np.polyval(m[2], t)

        ax.plot(x, y, z)

    # plot all points
    ax.scatter(p[0, 0], p[1, 0], p[2, 0], label='p', color='black')
    ax.scatter(pn[0, 0], pn[1, 0], pn[2, 0], label='pn', color='black')

    for g in goals:
        ax.scatter(g[0, 0], g[1, 0], g[2, 0], label='g', color='green')

    for point in path_points:
        ax.scatter(point[0, 0], point[1, 0], point[2, 0], label='ph', color='blue')

    # plot tangent vectors
    ax.quiver(pn[0][0], pn[1][0], pn[2][0], pn_prime[0][0], pn_prime[1][0],
              pn_prime[2][0], length=1,arrow_length_ratio=0.1, color='black', label='tangential vector')
    for i in range(len(path_points)):
        ax.quiver(path_points[i][0], path_points[i][1], path_points[i][2], tangential_vectors[i][0],
                  tangential_vectors[i][1], tangential_vectors[i][2], length=0.1, arrow_length_ratio=0.1, color='blue',
                  label='tangential vector')

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.legend()
    plt.show()
