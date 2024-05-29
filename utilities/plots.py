import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import norm

# delete this class if real time works
def plot_2d_curve(M, p, pn, pn_prime, goals, path_points, tangential_vectors):
    # Parameter
    t = np.linspace(0, 1, 100)

    # plot cubic polynomial
    x = []
    y = []
    for m in M:
        x = np.polyval(m[0], t)
        y = np.polyval(m[1], t)

        plt.plot(x, y)

    # plot all points
    plt.scatter(p[0], p[1], label='t-1', color='red')
    plt.scatter(pn[0], pn[1], label='t', color='black')

    i = 0
    for g in goals:
        lab = "Pg_" + str(i)
        plt.scatter(g[0], g[1], color='green')
        plt.text(g[0] - 0.1, g[1], f'{lab}')
        i += 1

    for point in path_points:
        plt.scatter(point[0], point[1], color='purple')

    # plot tangent vectors
    plt.quiver(pn[0], pn[1], pn_prime[0], pn_prime[1], scale=10, color='black', label='p\'')

    for i in range(len(path_points)):
        plt.quiver(path_points[i][0], path_points[i][1], tangential_vectors[i][0],
                   tangential_vectors[i][1],
                   color='purple', scale=10)

    plt.xlim(0, 1.5)
    plt.ylim(-0.6, 0.6)

    plt.title('model function')
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.grid(False)
    plt.legend()  # loc='lower left'
    plt.show()


def plot_3d_curve(data_3d, goals):
    p, pn, pn_prime, M, path_points, tangential_vectors = data_3d

    ax = plt.figure().add_subplot(projection='3d')
    t = np.linspace(0, 1, 100)

    # plot cubic polynomial
    for m in M:
        x = np.polyval(m[0], t)
        y = np.polyval(m[1], t)
        z = np.polyval(m[2], t)

        ax.plot(x, y, z)

    # plot all points
    ax.scatter(p[0], p[1], p[2], label='p', color='red')
    ax.scatter(pn[0], pn[1], pn[2], label='pn', color='black')

    for g in goals:
        ax.scatter(g[0], g[1], g[2], color='green')

    for point in path_points:
        ax.scatter(point[0], point[1], point[2], label='ph', color='blue')

    # plot tangent vectors
    ax.quiver(pn[0], pn[1], pn[2], pn_prime[0], pn_prime[1],
              pn_prime[2], length=0.1, normalize=True, arrow_length_ratio=0.2, color='black', label='p\'')

    for i in range(len(path_points)):
        ax.quiver(path_points[i][0], path_points[i][1], path_points[i][2], tangential_vectors[i][0],
                  tangential_vectors[i][1], tangential_vectors[i][2], length=0.1, normalize=True,
                  arrow_length_ratio=0.2, color='blue')

    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_zlabel('Z')
    ax.legend()
    plt.show()


def plot_normal_distribution(sigma, mu=0):
    # Create a range of x values
    x = np.linspace(-np.pi * 0.5, np.pi * 0.5, 100)

    # Plot the pdf
    plt.figure()
    plt.plot(x, norm.pdf(x, mu, sigma))
    # plt.title('Normal Distribution')
    plt.xlabel('x')
    # plt.ylabel('Probability Density')
    plt.show()
