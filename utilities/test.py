"""



    def update_curve_3d(self):
        self.ax1.cla()
        if self.data_3d:
            #unpack data
            p_previous = self.data_3d[0]
            p_current = self.data_3d[1]
            dp_current = self.data_3d[2]
            matrices = self.data_3d[3]

            x = []
            y = []
            z = []
            for m in matrices:
                x = np.polyval(m[0], self.ls_interval)
                y = np.polyval(m[1], self.ls_interval)
                z = np.polyval(m[2], self.ls_interval)
                self.ax1.plot(x, y, z)

            [self.ax1.scatter(g[0], g[1], color='green') for g in self.goal_positions]
            self.ax1.scatter(p_previous[0], p_previous[1], color='grey')
            self.ax1.scatter(p_current[0], p_current[1], color='black')

            self.ax1.set_xlim(0, 1.5)
            self.ax1.set_ylim(-0.8, 0.8)
            self.ax1.set_zlim(-0.4, 1.2)
            self.ax1.set_title("3D Parametric Curve")

    def update_curve_2d(self):
        self.ax2.cla()
        if self.data_3d:

            # unpack data
            p_previous = self.data_3d[0]
            p_current = self.data_3d[1]
            dp_current = self.data_3d[2]
            matrices = self.data_3d[3]

            x = []
            y = []
            for m in matrices:
                x = np.polyval(m[0], self.ls_interval)
                y = np.polyval(m[1], self.ls_interval)

                self.ax2.plot(x, y)

            [self.ax2.scatter(g[0], g[1], color='green') for g in self.goal_positions]
            self.ax2.scatter(p_previous[0], p_previous[1], color='black')
            self.ax2.scatter(p_current[0], p_current[1], color='black')

            self.ax2.set_xlim(0, 1.5)
            self.ax2.set_ylim(-0.6, 0.6)
            self.ax2.set_title("2D Parametric Curve")

"""