
import matplotlib.pyplot as plt
import numpy as np
from mpl_toolkits.mplot3d import Axes3D
from matplotlib.animation import FuncAnimation


class RealTimePlotter:
    def __init__(self, num_goals, active_goal_positions, goals_probability, goals_sample_quantity):
        self.num_goals = num_goals
        self.active_goal_positions = active_goal_positions
        self.goals_probability = goals_probability
        self.goals_sample_quantity = goals_sample_quantity

        # Set up the figure and axes
        self.fig = plt.figure(figsize=(12, 10))

        self.ax1 = self.fig.add_subplot(221)
        #self.ax2 = self.fig.add_subplot(222, projection='3d')
        #self.ax3 = self.fig.add_subplot(223)
        #self.ax4 = self.fig.add_subplot(224)

        # Initialize data structures for plots
        self.init_plots()



    def init_plots(self):
        # Plot 1: 2D points, vectors, and curves
        self.ax1.set_xlim(0, 1.5)
        self.ax1.set_ylim(-0.6, 0.6)
        self.p_previous, = self.ax1.plot([], [], 'bo')
        self.p_current, = self.ax1.plot([], [], 'ro')
        self.vectors = [self.ax1.quiver([], [], [], [], angles='xy', scale_units='xy', scale=1) for _ in
                        range(self.num_goals+1)]
        self.curves = [self.ax1.plot([], [], 'g')[0] for _ in range(self.num_goals)]

        """
        # Plot 2: 3D points, vectors, and curves
        self.ax2.set_xlim(-0.3, 1.3)
        self.ax2.set_ylim(-0.6, 0.6)
        self.ax2.set_zlim(-0.6, 0.6)
        self.point1_3d, = self.ax2.plot([], [], [], 'bo')
        self.point2_3d, = self.ax2.plot([], [], [], 'ro')
        self.vectors_3d = [self.ax2.quiver([], [], [], [], [], [], length=0.1, normalize=True) for _ in
                           range(self.num_vectors)]
        self.curves_3d = [self.ax2.plot([], [], [], 'g')[0] for _ in range(self.num_curves)]

        # Plot 3: Squares with data
        self.ax3.set_xlim(0, 1.5)
        self.ax3.set_ylim(-0.6, 0.6)
        self.squares = [self.ax3.add_patch(plt.Rectangle((0, 0), 0.1, 0.1, fill=None, edgecolor='r')) for _ in
                        range(self.num_squares)]
        self.square_texts = [self.ax3.text(0, 0, '') for _ in range(self.num_squares)]

        # Plot 4: Histogram
        self.hist_values = np.zeros(self.num_hist_bins)
        self.hist_bars = self.ax4.bar(range(self.num_hist_bins), self.hist_values)
        self.hist_texts = [self.ax4.text(i, 0, '') for i in range(self.num_hist_bins)]"""

    def update_plots(self, p_previous, p_current, model_data):
        # Unpack data
        # [0] direction vectors, [1] path points, [2] model matrix

        # Parameter
        t = np.linspace(0, 1, 100)

        # plot cubic polynomial
        for m in model_data[3]:
            x = np.polyval(m[0], t)
            y = np.polyval(m[1], t)

            plt.plot(x, y)

        # Update 2D points, vectors, and curves
        self.p_current.set_data(p_previous)
        self.p_previous.set_data(p_current)
        for vector, vec_data in zip(self.vectors, [model_data[1], [model_data[0]]]):
            vector.set_offsets([vec_data[0], vec_data[1]])
            vector.set_UVC([vec_data[2]], [vec_data[3]])
        for curve, curve_data in zip(self.curves, [x,y]):
            curve.set_data(curve_data[0], curve_data[1])

        """
        # Update 3D points, vectors, and curves
        self.point1_3d.set_data(points_3d[0][0], points_3d[0][1])
        self.point1_3d.set_3d_properties(points_3d[0][2])
        self.point2_3d.set_data(points_3d[1][0], points_3d[1][1])
        self.point2_3d.set_3d_properties(points_3d[1][2])
        for vector, vec_data in zip(self.vectors_3d, vectors_3d):
            vector.remove()
            vector = self.ax2.quiver(vec_data[0], vec_data[1], vec_data[2], vec_data[3], vec_data[4], vec_data[5],
                                     length=0.1, normalize=True)
        for curve, curve_data in zip(self.curves_3d, curves_3d):
            curve.set_data(curve_data[0], curve_data[1])
            curve.set_3d_properties(curve_data[2])

        # Update squares and their data
        for square, square_text, square_data in zip(self.squares, self.square_texts, squares_data):
            square.set_xy((square_data[0], square_data[1]))
            square.set_width(square_data[2])
            square.set_height(square_data[3])
            square_text.set_position((square_data[0], square_data[1]))
            square_text.set_text(square_data[4])

        # Update histogram
        for bar, height, text, value in zip(self.hist_bars, hist_data, self.hist_texts, range(len(hist_data))):
            bar.set_height(height)
            text.set_position((value, height))
            text.set_text(str(height))"""

        plt.draw()

    def start(self, update_func, interval=100):
        self.animation = FuncAnimation(self.fig, update_func, interval=interval)
        plt.show()
