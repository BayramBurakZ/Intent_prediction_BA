import numpy as np


class PredictionModel:
    """ A class that calculates predicted trajectories for each goal.

    Attributes:
        p_previous, p_current: (NDArray[np.float64])    two measured points of the hand wrist at given time
        t_previous, t_current: (int)                    timestamp of the two points
        dp_previous, dp_current: (NDArray[np.float64])  directional vector at each point
    """

    def __init__(self, sample_min_distance, animated_plots, activate_plotter):
        """ Constructor for PredictionModel class.

        :param sample_min_distance: (float)     min distant to start modelling trajectories
        :param animated_plots: (AnimatedPlots)  instance for animating data
        :param activate_plotter: (bool)         activates the real time plotter
        """
        self.p_previous = None
        self.p_current = None

        self.dp_previous = None
        self.dp_current = None

        self.sample_min_distance = sample_min_distance
        self.animated_plots = animated_plots

        self.activate_plotter = activate_plotter

    def calculate_predicted_direction(self, p_next, goal_positions):
        """ Calculates the predicted directions for each goal by modeling a cubic polynomial curve in 3D space.

        :param p_next: (NDArray[np.float64])    last measured point of the hand wrist
        :param goal_positions: (list)           position of all goals

        :return: (NDArray[np.float64])  predicted direction of each goal
        """

        # wait for first three measurements to start calculating
        if self.p_previous is None:
            self.p_previous = p_next
            return

        if self.p_current is None:
            self.p_current = p_next
            self.dp_current = position_derivative(self.p_previous, self.p_current)
            return

        # only calculate after minimum distance between measurements is reached
        if distance(self.p_current, p_next) < self.sample_min_distance:
            return

        # shift coordinates, timestamps and derivative
        self.p_previous = self.p_current
        self.p_current = p_next
        self.dp_previous = self.dp_current
        self.dp_current = position_derivative(self.p_previous, self.p_current)

        # save predicted trajectories and it's derivatives for each goal as matrices
        prediction_mats = []
        deriv_prediction_mats = []

        for goal in goal_positions:
            m = prediction_model_matrices(self.p_previous, self.dp_previous, np.array([goal[0], goal[1], goal[2]]))
            prediction_mats.append(m[0])
            deriv_prediction_mats.append(m[1])

        # approximate progress on trajectory and calculate the corresponding directional vector
        predicted_path_points = []
        deriv_at_path_points = []

        for i in range(len(goal_positions)):
            s = calculate_path_coordinate(self.p_previous, self.p_current, goal_positions[i])
            predicted_path_points.append(calculate_polynomial(prediction_mats[i], s))
            deriv_at_path_points.append(normalize(calculate_polynomial(deriv_prediction_mats[i], s)))

        # plot the trajectories with directional vectors
        if self.activate_plotter:
            self.animated_plots.update_data(
                data_3d=[self.p_previous, self.p_current, self.dp_current, prediction_mats, predicted_path_points,
                         deriv_at_path_points])

        return deriv_at_path_points


def position_derivative(p1, p2):
    """ Calculates the normalized direction vector of two points. """
    return normalize(p2 - p1)


def normalize(p):
    """ Normalizes a vector. """
    divisor = np.linalg.norm(p)
    return p if divisor == 0 else p / np.linalg.norm(p)


def calculate_path_coordinate(p_previous, p_current, p_goal):
    """ Calculates the normalized path coordinate as point on the trajectory.

    :param p_previous: (NDArray[np.float64])    measured point at t_n-1
    :param p_current: (NDArray[np.float64])     measured point at t_n
    :param p_goal: (NDArray[np.float64])        position of goal

    :return: predicted path coordinate
    """
    distance_a = np.linalg.norm(p_current - p_previous)
    distance_b = np.linalg.norm(p_goal - p_current)
    return distance_a / (distance_a + distance_b)


def calculate_polynomial(matrix, s):
    """ Calculates the value of a polynomial at point s. """
    x = np.polyval(matrix[0], s)
    y = np.polyval(matrix[1], s)
    z = np.polyval(matrix[2], s)

    return np.array([x, y, z])


def prediction_model_matrices(p_previous, dp_previous, p_goal):
    """ Calculates the coefficients of the trajectory model and it's derivative.

    :param p_previous: (NDArray[np.float64])      measured point at t_n-1
    :param dp_previous: (NDArray[np.float64])     derivative of p
    :param p_goal: (NDArray[np.float64])          position of goal

    :return: coefficient matrix of the trajectory model, and it's derivative as a tuple
    """

    # parameters of cubic polynomial
    a0 = np.array(p_previous, copy=True)
    a1 = np.array(dp_previous, copy=True)
    a2 = 1.5 * p_goal - 1.5 * p_previous - 1.5 * dp_previous
    a3 = -0.5 * p_goal + 0.5 * p_previous + 0.5 * dp_previous

    # coefficients of cubic polynom as 3x4 matrix
    prediction_mat = np.zeros((3, 4))
    for i in range(3):
        prediction_mat[i] = [a3[i], a2[i], a1[i], a0[i]]

    # coefficients of first derivative cubic polynom as 3x3 matrix
    deriv_prediction_mat = np.zeros((3, 3))
    for i in range(3):
        deriv_prediction_mat[i] = [3 * a3[i], 2 * a2[i], a1[i]]

    '''
    # coefficients of second derivative cubic polynom 3x3 matrix
    Ma = np.zeros((3, 2))
    for i in range(3):
        Ma[i] = [6 * a3[i, 0], 2 * a2[i, 0]]
    '''
    return prediction_mat, deriv_prediction_mat


def distance(v1, v2):
    """ Calculates the Euclidean distance between two vectors. """
    return np.linalg.norm(v1 - v2)
