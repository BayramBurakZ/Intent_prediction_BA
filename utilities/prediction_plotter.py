import os

import matplotlib.pyplot as plt
import numpy as np


def plot_2d_curve(goals, prev_p, curr_p, curr_dp):

    # Parameter
    t = np.linspace(0, 1, 100)

    # plot cubic polynomial
    x = []
    y = []
    for g in goals:
        # predicted curve
        x = np.polyval(g.mat[0], t)
        y = np.polyval(g.mat[1], t)

        plt.plot(x, y)

        # goal position
        plt.scatter(g.pos[0], g.pos[1], color='green')
        plt.text(g.pos[0] - 0.05, g.pos[1], f'{str(g.num)}')

        # progress
        plt.scatter(g.ppt[0], g.ppt[1], color='purple')

        # tangential vectors
        plt.quiver(g.ppt[0], g.ppt[1], g.dppt[0], g.dppt[1], color='purple', scale=10)

    # plot all points
    plt.scatter(prev_p[0], prev_p[1], label='t-1', color='red')
    plt.scatter(curr_p[0], curr_p[1], label='t', color='black')

    # plot tangent vectors
    plt.quiver(curr_p[0], curr_p[1], curr_dp[0], curr_dp[1], scale=10, color='black', label='p\'')

    plt.xlim(0.0, 1.0)
    plt.ylim(-0.6, 0.6)
    plt.xticks([])
    plt.yticks([])

    plt.grid(False)
    plt.show()


def plot_3d_curve(goals, prev_p, curr_p, curr_dp):

    fig = plt.figure()
    ax = fig.add_subplot(111, projection='3d')

    # Parameter
    t = np.linspace(0, 1, 100)

    # Plot cubic polynomial
    for g in goals:
        # Predicted curve
        x = np.polyval(g.mat[0], t)
        y = np.polyval(g.mat[1], t)
        z = np.polyval(g.mat[2], t)

        ax.plot(x, y, z)

        # Goal position
        ax.scatter(g.pos[0], g.pos[1], g.pos[2], color='green')

        # Progress
        ax.scatter(g.ppt[0], g.ppt[1], g.ppt[2], color='purple')

        # Tangential vectors
        ax.quiver(g.ppt[0], g.ppt[1], g.ppt[2], np.polyval(g.dmat[0], g.ppt[0]),
                  np.polyval(g.dmat[1], g.ppt[1]), np.polyval(g.dmat[2], g.ppt[2]),
                  color='purple', length=0.1, normalize=True)

    # Plot all points
    ax.scatter(prev_p[0], prev_p[1], prev_p[2], label='t-1', color='red')
    ax.scatter(curr_p[0], curr_p[1], curr_p[2], label='t', color='black')

    # Plot tangent vectors
    ax.quiver(curr_p[0], curr_p[1], curr_p[2], curr_dp[0], curr_dp[1], curr_dp[2],
              length=0.1, normalize=True, color='black', label='p\'')

    ax.set_xlim(0.3, 1.0)
    ax.set_ylim(-0.6, 0.6)
    ax.set_zlim(0.0, 0.5)

    ax.grid(False)

    plt.show()
