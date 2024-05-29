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
        self.ax2.set_xlim(0, 1.1)
        self.ax2.set_ylim(-0.6, 0.6)

        # histogram plot
        self.ax3 = self.fig.add_subplot(133)
        self.bars = None
        self.texts = []

    def update_data(self, data_3d=None, data_bar=None):
        if data_3d is not None:
            self.data_3d = data_3d
        if data_bar is not None:
            self.data_bar = data_bar
        plt.pause(0.01)

    def update_plot(self, frame):
        self.update_curves_2d_3d()
        self.update_bar()

    def update_curves_2d_3d(self):
        self.ax1.cla()
        self.ax2.cla()
        if self.data_3d:
            # unpack data
            p_previous, p_current, dp_current, matrices, path_points, d_path_points = self.data_3d

            for m in matrices:
                x = np.polyval(m[0], self.ls_interval)
                y = np.polyval(m[1], self.ls_interval)
                z = np.polyval(m[2], self.ls_interval)

                self.ax1.plot(x, y, z, color="black")
                self.ax2.plot(x, y, color="black")

            [self.ax1.scatter(g[0], g[1], color='green') for g in self.goal_positions],
            self.ax1.scatter(p_previous[0], p_previous[1], color='red'),
            self.ax1.scatter(p_current[0], p_current[1], color='red')

            [self.ax2.scatter(g[0], g[1], color='green') for g in self.goal_positions],
            self.ax2.scatter(p_previous[0], p_previous[1], color='red'),
            self.ax2.scatter(p_current[0], p_current[1], color='red')

            [self.ax2.scatter(p[0], p[1], color='blue') for p in path_points]

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

    def update_bar(self):
        self.ax3.cla()
        if self.data_bar:
            # unpack
            goal_ids,probabilities,sample_quantity,distance,uncat_goal,current_time = self.data_bar

            # if len(goal_ids) == 0 or len(probabilities) == 0 or len(sample_quantity) == 0 or len(distance) == 0:
            # return

            x = goal_ids
            y = [prob * 100 for prob in probabilities]
            self.ax3.set_ylim(0, 100)

            self.bars = self.ax3.bar(x, y, width=0.8)
            self.ax3.set_xlim(min(goal_ids) - 0.5, max(goal_ids) + 0.5)
            self.ax3.set_title("Bar Plot")

            # Set x-ticks and labels
            self.ax3.set_xticks(x)
            self.ax3.set_xticklabels([f'{goal}\n{dist:.2f}' for goal, dist in zip(goal_ids, distance)])

            # Create a secondary x-axis for the upper labels
            sec_ax = self.ax3.secondary_xaxis('top')
            sec_ax.set_xticks(x)
            sec_ax.set_xticklabels([f'{goal}\n{sample}' for goal, sample in zip(goal_ids, sample_quantity)])

            # Adding a custom legend
            legend_label1 = f'upperX: sample/id \nlowerX: distance/id \nY: probability'
            legend_label2 = f'Time: {current_time} \nUncategorized goal: {uncat_goal:.2f}%'
            self.ax3.text(0.95, 0.95, legend_label1, transform=self.ax3.transAxes, ha='right', va='top')

            self.ax3.text(0.05, 0.95, legend_label2, transform=self.ax3.transAxes, ha='left', va='top')

            # Adjusting plot to fit lower text
            self.ax3.margins(y=0.2)
            self.ax3.figure.tight_layout()

            self.ax3.margins(y=0.2)

    def animate(self):
        self.ani = FuncAnimation(self.fig, self.update_plot, frames=25, interval=40, repeat=False,)
        plt.tight_layout()
        plt.show(block=False)

    def on_close(self, event):
        sys.exit("EXiT")
