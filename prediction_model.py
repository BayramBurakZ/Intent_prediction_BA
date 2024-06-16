import numpy as np


class PredictionModel:
    """ A class that calculates predicted trajectories for each goal.

    Attributes:
        goals (List)                                    List of goal instances
        prev_p, curr_p: (NDArray[np.float64])           two measured points of the hand wrist at given time
        prev_dp, curr_dp: (NDArray[np.float64])         directional vector at each point
    """

    def __init__(self, goals, min_dist, min_prog):
        """
        :param min_dist: (float)     minimum distance to use lower boundary
        :param min_prog: (float)     minimum prediction progression as lower boundary
        """
        self.goals = goals

        self.prev_p = None
        self.curr_p = None
        self.prev_dp = None
        self.curr_dp = None

        self.min_dist = min_dist
        self.min_prog = min_prog

    def update(self, next_p):
        """ Calculates the predicted directions for each goal by modeling a cubic polynomial curve in 3D space.
        :param next_p: (NDArray[np.float64])    last measured point of the hand wrist
        """

        # calculating starts after third measurement
        if self.prev_p is None:
            self.prev_p = next_p
            return

        if self.curr_p is None:
            self.curr_p = next_p
            self.curr_dp = point_direction(self.prev_p, self.curr_p)
            return

        # calculating starts after minimum distance between measurements is reached
        if distance(self.curr_p, next_p) < self.min_dist:
            return

        # shift coordinates, timestamps and derivative
        self.prev_p = self.curr_p
        self.curr_p = next_p
        self.prev_dp = self.curr_dp
        self.curr_dp = point_direction(self.prev_p, self.curr_p)

        # set the distance from current point to goal
        [g.set_distance(self.curr_p) for g in self.goals]

        # set model trajectory and its derivative as matrices
        [g.set_matrices(calc_mats(self.prev_p, self.prev_dp, g.pos)) for g in self.goals]

        # set the progression of the current point at the trajectory path
        [g.set_progression(max(calc_progression(self.prev_p, self.curr_p, g.pos), self.min_prog)) for g in self.goals]

        # set angles between measured and predicted direction
        [setattr(g, 'angle', calc_angle(g.dppt, self.curr_dp)) for g in self.goals]


def point_direction(p1, p2):
    """ Calculates the normalized direction vector of two points. """
    p = p2 - p1
    divisor = np.linalg.norm(p)
    return p if divisor == 0 else p / np.linalg.norm(p)


def calc_progression(prev_p, curr_p, goal):
    """ Calculates the normalized path coordinate as point on the trajectory.

    :param prev_p: (NDArray[np.float64])    measured point at t_n-1
    :param curr_p: (NDArray[np.float64])    measured point at t_n
    :param goal: (NDArray[np.float64])      position of goal

    :return: predicted path coordinate
    """
    distance_a = np.linalg.norm(curr_p - prev_p)
    distance_b = np.linalg.norm(goal - curr_p)
    return distance_a / (distance_a + distance_b)


def calc_mats(prev_p, prev_dp, goal):
    """ Calculates the coefficients of the trajectory model and it's derivative.

    :param prev_p: (NDArray[np.float64])    measured point at t_n-1
    :param prev_dp: (NDArray[np.float64])   derivative of p
    :param goal: (NDArray[np.float64])      position of goal

    :return: coefficient matrix of the trajectory model, and it's derivative as a tuple
    """

    # parameters of cubic polynomial
    a0 = np.array(prev_p, copy=True)
    a1 = np.array(prev_dp, copy=True)
    a2 = 1.5 * goal - 1.5 * prev_p - 1.5 * prev_dp
    a3 = -0.5 * goal + 0.5 * prev_p + 0.5 * prev_dp

    # coefficients of cubic polynom as 3x4 matrix
    prediction_mat = np.zeros((3, 4))
    for i in range(3):
        prediction_mat[i] = [a3[i], a2[i], a1[i], a0[i]]

    # coefficients of first derivative cubic polynom as 3x3 matrix
    deriv_prediction_mat = np.zeros((3, 3))
    for i in range(3):
        deriv_prediction_mat[i] = [3 * a3[i], 2 * a2[i], a1[i]]

    """
    # coefficients of second derivative cubic polynom 3x3 matrix
    Ma = np.zeros((3, 2))
    for i in range(3):
        Ma[i] = [6 * a3[i, 0], 2 * a2[i, 0]]
    """
    return prediction_mat, deriv_prediction_mat


def distance(v1, v2):
    """ Calculates the Euclidean distance between two vectors. """
    return np.linalg.norm(v1 - v2)


def calc_angle(v1, v2):
    """ Calculates the angle on x,y plane between two 3D vectors. """

    # remove z component
    v1 = np.array([v1[0], v1[1]])
    v2 = np.array([v2[0], v2[1]])

    # calculate angle
    dot = np.dot(v1, v2)
    v1_norm = np.linalg.norm(v1)
    v2_norm = np.linalg.norm(v2)

    if np.isclose(v1_norm, 0, 0.001) or np.isclose(v2_norm, 0, 0.001):
        return np.pi

    cos_angle = dot / (v1_norm * v2_norm)

    # for numerical precision
    cos_angle = np.clip(cos_angle, -1.0, 1.0)

    return np.arccos(cos_angle)  # in radiance
