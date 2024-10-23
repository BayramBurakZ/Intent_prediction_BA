import numpy as np


class Goal:
    """
    A class that represents a goal.

    Attributes:
        num (int): The ID of the goal.
        pos (numpy.ndarray): The coordinates of the goal.

        dist (float): The distance to the last measured hand wrist position.
        prev_dist (float): The distance to the previous measured hand wrist position.
        mat (numpy.ndarray): The trajectory to the goal as a matrix.
        dmat (numpy.ndarray): The derivative of the trajectory matrix.
        ppt (numpy.ndarray): The predicted point on the trajectory.
        dppt (numpy.ndarray): The derivative at the predicted point.
        angle (float): The angle between the last measured direction and the predicted direction.
        hand_towards_goal (bool): True if hand is moving towards. False otherwise.

        prob (float): The accumulated probability of samples.
        sq (int): The sample quantity.
    """

    def __init__(self, number: int, position: np.ndarray) -> None:
        self.num = number
        self.pos = position

        # prediction model
        self.dist = 10000.0  # default to np.inf caused divide by zero error
        self.prev_dist = 10000.0
        self.mat = None
        self.dmat = None
        self.ppt = None
        self.dppt = None
        self.angle = np.pi
        self.hand_towards_goal = False

        # probability
        self.prob = 0.0
        self.sq = 0

    def set_distance(self, curr_p: np.ndarray) -> None:
        self.prev_dist = self.dist
        self.dist = np.linalg.norm(curr_p - self.pos)

    def set_matrices(self, mats: tuple[np.ndarray, np.ndarray]) -> None:
        self.mat = mats[0]
        self.dmat = mats[1]

    def set_progression(self, progression: float) -> None:
        """
        Parameters:
            progression (float): The progression along the trajectory.
        """
        self.ppt = calc_poly(self.mat, progression)
        self.dppt = calc_poly(self.dmat, progression)

        # NOTE: This has been added after Tests.
        self.dppt = norm_vector(self.dppt)

    def update_probability(self, angle_probability: float) -> None:
        """
        Updates probability of Goal with the last calculated probability of angle.

        Parameters:
            angle_probability (float): The probability of the last measured angle.
        """

        min_probability = 0.001  # lower boundary of 0.1% for the angle probability to reset the goal probability

        if angle_probability < min_probability or not self.hand_towards_goal:  # reset
            self.prob = 0.0
            self.sq = 0

        elif self.prob < min_probability:  # begin
            self.prob = angle_probability
            self.sq = 1

        else:  # update
            self.prob *= angle_probability
            self.sq += 1

    def divide_probability(self, divisor: float) -> None:
        self.prob /= divisor

    def to_dict_element(self) -> dict:
        """ Convert object into dict element with relevant data. """
        return {
            self.num: {
                "position": self.pos.tolist(),
                "probability": round(self.prob * 100, 2),
                "distance": round(self.dist, 2),
                "sample_quantity": self.sq
            }
        }

    @staticmethod
    def goals_list_to_dict(goals_list):
        """ Convert a list of goal objects into a dictionary """
        combined_dict = {}
        for goal in goals_list:
            combined_dict.update(goal.to_dict_element())
        return combined_dict


def calc_poly(matrix: np.ndarray, s: float) -> np.ndarray:
    """ Calculates the value of a polynomial at point s. """
    x = np.polyval(matrix[0], s)
    y = np.polyval(matrix[1], s)
    z = np.polyval(matrix[2], s)

    return np.array([x, y, z])


def norm_vector(vector: np.ndarray, epsilon: float = 0.0001) -> np.ndarray:
    """ Norm a vector. """
    length = np.linalg.norm(vector)
    if length < epsilon:
        return vector

    return vector / length
