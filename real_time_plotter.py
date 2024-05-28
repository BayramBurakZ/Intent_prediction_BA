import sys

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.animation import FuncAnimation


class AnimatedPlots:
    def __init__(self, goal_positions, ls_interval=100):
        self.goal_positions = goal_positions

        self.ls_interval = np.linspace(0, 1, ls_interval)
        self.data_3d = []
        self.data_bar = []

        # figure for plots
        self.fig = plt.figure(figsize=(24, 12))
        self.fig.canvas.mpl_connect('close_event', self.on_close)

        # 3D plot
        self.ax1 = self.fig.add_subplot(131, projection='3d')
        self.ax1.set_xlim(0, 1.5)
        self.ax1.set_ylim(-0.7, 0.7)
        self.ax1.set_zlim(-0.4, 1.2)

        # 2D plot
        self.ax2 = self.fig.add_subplot(132)
        self.ax2.set_xlim(0, 1.5)
        self.ax2.set_ylim(-0.7, 0.7)

        # histogram plot
        self.ax3 = self.fig.add_subplot(133)
        self.bars = None

    def update_data(self, data_3d=None, data_bar=None):
        if data_3d is not None:
            self.data_3d = data_3d
        if data_bar is not None:
            self.data_bar = data_bar

    def update_plot(self, frame):
        self.update_curves_2d_3d()
        # self.update_histogram()

    def update_curves_2d_3d(self):
        self.ax1.cla()
        self.ax2.cla()
        if self.data_3d:
            # unpack data
            p_previous = self.data_3d[0]
            p_current = self.data_3d[1]
            dp_current = self.data_3d[2]
            matrices = self.data_3d[3]
            path_points = self.data_3d[4]
            d_path_points = self.data_3d[5]

            x = []
            y = []
            z = []
            for m in matrices:
                x = np.polyval(m[0], self.ls_interval)
                y = np.polyval(m[1], self.ls_interval)
                z = np.polyval(m[2], self.ls_interval)

                self.ax1.plot(x, y, z, color="black")
                self.ax2.plot(x, y, color="black")

            scatter_plot = lambda ax, goal_positions, p_previous, p_current: (
                [ax.scatter(g[0], g[1], color='green') for g in goal_positions],
                ax.scatter(p_previous[0], p_previous[1], color='red'),
                ax.scatter(p_current[0], p_current[1], color='red')
            )
            scatter_plot(self.ax1, self.goal_positions, p_previous, p_current)
            scatter_plot(self.ax2, self.goal_positions, p_previous, p_current)

            [self.ax2.scatter(p[0], p[1], color='green') for p in path_points]

            # plot tangent vectors

            for i in range(len(path_points)):
                self.ax2.quiver(path_points[i][0], path_points[i][1], d_path_points[i][0], d_path_points[i][1],
                                color='blue', scale=5, width=0.005)

            self.ax2.quiver(p_current[0], p_current[1], dp_current[0], dp_current[1], scale=5, color='red',
                            width=0.01)

            self.ax1.set_xlim(0, 1.5)
            self.ax1.set_ylim(-0.7, 0.7)
            self.ax1.set_zlim(-0.4, 1.1)
            self.ax1.set_title("3D Parametric Curve")

            self.ax2.set_xlim(0, 1.5)
            self.ax2.set_ylim(-0.7, 0.7)
            self.ax2.set_title("2D Parametric Curve")

    def update_histogram(self):
        self.ax3.cla()
        if self.data_bar:
            x = np.arange(len(self.data_bar))

            if self.bars is None:
                self.bars = self.ax3.bar(x, self.data_bar)
            else:
                for bar, height in zip(self.bars, self.data_bar):
                    bar.set_height(height)
            self.ax3.set_title("Bar Plot")

    def animate(self):
        self.ani = FuncAnimation(self.fig, self.update_plot, frames=25, interval=200, repeat=False)
        plt.tight_layout()
        plt.show(block=False)

    def on_close(self, event):
        sys.exit("EXiT")
