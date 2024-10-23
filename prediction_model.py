import numpy as np
from data_handler import DataHandler


class PredictionModel:
    """
    A class that calculates predicted trajectories for each goal.

    Attributes:
        prev_p (numpy.ndarray): Measured point of the hand wrist at time t-1.
        curr_p (numpy.ndarray): Measured point of the hand wrist at time t.
        prev_dp (numpy.ndarray): Directional vector at time t-1.
        curr_dp (numpy.ndarray): Directional vector at time t.
    """

    def __init__(self, data_handler: DataHandler, MODEL_PARAMS: tuple[float, float]) -> None:
        """
        Parameters:
            data_handler (DataHandler): An instance for handling the data during runtime.
            MODEL_PARAMS (tuple): A tuple specifying
                [0] min_distance (float): The minimum distance at which to begin calculations.
                [1] min_progression (float): The minimum progression along the predicted trajectory.
        """

        self.data_handler = data_handler

        self.prev_p = None
        self.curr_p = None
        self.prev_dp = None
        self.curr_dp = None

        self.MIN_DIST = MODEL_PARAMS[0]
        self.MIN_PROG = MODEL_PARAMS[1]

    def update(self, next_p: np.ndarray) -> None:
        """
        Calculates the predicted directions for each goal by modeling a cubic polynomial curve in 3D space.

        Parameters:
            next_p (numpy.ndarray): Last measured point of the hand wrist.
        """

        # Gets possible goals when database (action) is used. All goals otherwise.
        goals = self.data_handler.get_goals()

        # calculating starts after third measurement
        if self.prev_p is None:
            self.prev_p = next_p
            return

        if self.curr_p is None:
            self.curr_p = next_p
            self.curr_dp = point_direction(self.prev_p, self.curr_p)
            return

        # calculating starts after minimum distance between measurements is reached
        if distance(self.curr_p, next_p) < self.MIN_DIST:
            return

        # shift coordinates, timestamps and derivative
        self.prev_p = self.curr_p
        self.curr_p = next_p
        self.prev_dp = self.curr_dp
        self.curr_dp = point_direction(self.prev_p, self.curr_p)

        self.data_handler.set_pm_data(True, self.prev_p, self.curr_p, self.prev_dp, self.curr_dp)

        for g in goals:
            # Set the distance from current point to goal
            g.set_distance(self.curr_p)

            # Set model trajectory and its derivative as matrices
            g.set_matrices(calc_mats(self.prev_p, self.prev_dp, g.pos))

            # Set the progression of the current point at the trajectory path
            g.set_progression(max(calc_progression(self.prev_p, self.curr_p, g.pos), self.MIN_PROG))

            # Set angles between measured and predicted direction
            g.angle = calc_angle(g.dppt, self.curr_dp)

            # Calculate if Hand is moving towards target.
            g.hand_towards_goal = calc_hand_towards_goal(g.pos, self.curr_p, self.curr_dp)


def point_direction(p1: np.ndarray, p2: np.ndarray) -> np.ndarray:
    """
    Calculates the normalized direction vector between two points.
    """

    p = p2 - p1
    divisor = np.linalg.norm(p)
    return p if divisor < 1e-10 else p / divisor


def calc_progression(prev_p: np.ndarray, curr_p: np.ndarray, goal_pos: np.ndarray) -> float:
    """
    Calculates the normalized path coordinate (progression) as a point on the trajectory.

    Parameters:
        prev_p (numpy.ndarray): Measured point at time t_n-1.
        curr_p (numpy.ndarray): Measured point at time t_n.
        goal_pos (numpy.ndarray): Position of the goal.

    Returns:
        float: The predicted path coordinate.
    """

    distance_a = np.linalg.norm(curr_p - prev_p)
    distance_b = np.linalg.norm(goal_pos - curr_p)
    denominator = distance_a + distance_b

    if denominator < 1e-10:
        return 0.0
    return distance_a / denominator


def calc_mats(prev_p: np.ndarray, prev_dp: np.ndarray, goal_pos: np.ndarray) -> tuple[np.ndarray, np.ndarray]:
    """
    Calculates the coefficients of the trajectory model and its derivative.

    Parameters:
        prev_p (numpy.ndarray): Measured point at time t_n-1.
        prev_dp (numpy.ndarray): Derivative of the point.
        goal_pos (numpy.ndarray): Position of the goal.

    Returns:
        tuple: A tuple containing the coefficient matrix of the trajectory model and its derivative.
    """

    # parameters of cubic polynomial
    a0 = np.array(prev_p, copy=True)
    a1 = np.array(prev_dp, copy=True)
    a2 = 1.5 * goal_pos - 1.5 * prev_p - 1.5 * prev_dp
    a3 = -0.5 * goal_pos + 0.5 * prev_p + 0.5 * prev_dp

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


def distance(v1: np.ndarray, v2: np.ndarray) -> float:
    """
    Calculates the Euclidean distance between two vectors.
    """
    return np.linalg.norm(v1 - v2)


def calc_angle(v1: np.ndarray, v2: np.ndarray) -> float:
    """
    Calculates the angle on the x,y plane between two 3D vectors.
    """

    # Project vectors onto the x-y plane by ignoring z component
    v1_xy = np.array([v1[0], v1[1]])
    v2_xy = np.array([v2[0], v2[1]])

    # Calculate the angle using atan2
    angle = np.arctan2(np.linalg.det([v1_xy, v2_xy]), np.dot(v1_xy, v2_xy))

    return abs(angle)


def calc_hand_towards_goal(goal_position: np.ndarray, hand_position: np.ndarray, hand_direction: np.ndarray) -> bool:
    """
    Calculates whether hand is moving towards point goal.

    Parameters:
        goal_position (numpy.ndarray):  Position of goal.
        hand_position (numpy.ndarray):  Position of hand.
        hand_direction (numpy.ndarray): Direction hand is moving.

    Returns:
        bool: True if hand is moving towards goal, False otherwise.
    """

    difference_vector = goal_position - hand_position
    return np.dot(difference_vector, hand_direction) > 0
