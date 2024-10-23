import numpy as np
from scipy import stats

from data_handler import DataHandler


class ProbabilityEvaluator:
    """
    A class that evaluates the probability of each goal.
    """

    def __init__(self, data_handler: DataHandler, PROBABILITY_PARAMS: tuple[float, float, float]) -> None:
        """
        Parameters:
            data_handler (DataHandler): An instance for handling the data during runtime.
            PROBABILITY_PARAMS (tuple): A tuple specifying
                [0] variance_lower_limit (float): The lower bound for variance in the normal distribution.
                [1] variance_upper_limit (float): The upper bound for variance in the normal distribution.
                [2] omega (float): A parameter used in the cost function to adjust probabilities.
        """

        self.data_handler = data_handler
        self.MIN_VARIANCE = PROBABILITY_PARAMS[0]
        self.MAX_VARIANCE = PROBABILITY_PARAMS[1]
        self.OMEGA = PROBABILITY_PARAMS[2]

    def update(self) -> None:
        """
        Calculates the probability of goals by evaluating predicted angles.
        """

        # Gets possible goals when database (action) is used. All goals otherwise.
        goals = self.data_handler.get_goals()

        # Angles between measured direction and predicted directions of goals.
        angles = [g.angle for g in goals]

        # calculates standard deviation of all angles.
        sd_of_angles = calc_sd(angles, self.MIN_VARIANCE, self.MAX_VARIANCE)

        # update probability with normal PDF of angle.
        for g in goals:
            g.update_probability(stats.norm.pdf(g.angle, 0, sd_of_angles))

        # apply distance cost function
        dist_cost_function(goals, self.OMEGA)

        # normalize probability of goals.
        norm_divisor = max(1, sum(g.prob for g in goals))
        for g in goals:
            g.divide_probability(norm_divisor)


def dist_cost_function(goals, omega: float = 1.0) -> None:
    """
    Applies a cost function to the current probability to account for the distance between goals,
    thereby refining the probability calculation.

    Parameters:
        goals (list[Goal]): List of all goals.
        omega (float): weight for the cost function.
    """
    for g in goals:
        g.divide_probability(1 + omega * g.dist)


def calc_sd(angles: list[float], min_variance: float, max_variance: float) -> float:
    """
    Calculates the standard deviation of angles.

    Parameters:
        angles (list): List of angles of between measured direction vector and the predicted direction vectors.
        min_variance (float): The lower limit for variance in the normal distribution.
        max_variance (float): The upper limit for variance in the normal distribution.

    Returns:
        float: The standard deviation between the angles.
    """

    sigma = np.std(angles)

    # boundaries for standard deviation
    min_sd = np.sqrt(min_variance)
    max_sd = np.sqrt(max_variance)

    return max(min_sd, min(sigma, max_sd))
