import numpy as np
from scipy import stats


class ProbabilityEvaluator:
    """
    A class that evaluates the probability of each goal.
    """

    def __init__(self, goals, VARIANCE_BOUNDS):
        """
        Parameters:
            goals (list[Goals]): A list of instances of the Goals class.
            VARIANCE_BOUNDS (tuple): A tuple specifying the lower and upper limits for variance in the normal distribution.
        """

        self.goals = goals
        self.MIN_VARIANCE = VARIANCE_BOUNDS[0]
        self.MAX_VARIANCE = VARIANCE_BOUNDS[1]

    def update(self):
        """
        Calculates the probability of goals by evaluating predicted angles.
        """

        angles = [g.angle for g in self.goals]

        # calculates standard deviation of all angles
        sd_of_angles = calc_sd(angles, self.MIN_VARIANCE, self.MAX_VARIANCE)

        # update probability with normal PDF of angle
        for g in self.goals:
            g.update_probability(stats.norm.pdf(g.angle, 0, sd_of_angles))

        # normalize probability of goals
        norm_divisor = max(1, sum(g.prob for g in self.goals))
        for g in self.goals:
            g.normalize_probability(norm_divisor)


def calc_sd(angles, min_variance, max_variance):
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
