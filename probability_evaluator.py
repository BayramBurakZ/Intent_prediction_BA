import numpy as np
from scipy import stats


class ProbabilityEvaluator:
    """ A class that evaluates the probability of each goal."""

    def __init__(self, goals, min_variance, max_variance):
        """
        :param goals: (list)                    List of goal instances
        :param min_variance: (float)            lower limit for variance in normal distribution
        :param max_variance: (float)            upper limit for variance in normal distribution
        """
        self.goals = goals
        self.min_variance = min_variance
        self.max_variance = max_variance

    def update(self):
        """ Calculates the probability of goals by evaluating predicted angles."""

        angles = [g.angle for g in self.goals]

        # calculates standard deviation of all angles
        sd_of_angles = calc_sd(angles, self.min_variance, self.max_variance)

        # update probability with normal PDF of angle
        [g.update_probability(stats.norm.pdf(g.angle, 0, sd_of_angles)) for g in self.goals]

        # normalize probability of goals
        norm_divisor = max(1, sum(g.prob for g in self.goals))
        [g.normalize_probability(norm_divisor) for g in self.goals]


def calc_sd(angles, min_variance, max_variance):
    """ Calculates the standard deviation of angles.

    :param angles: (list)           angles of predicted direction vector
    :param min_variance: (float)    lower limit for variance in normal distribution
    :param max_variance: (float)    upper limit for variance in normal distribution

    :return: (float)    standard deviation between angles
    """
    sigma = np.std(angles)

    # boundaries for standard deviation
    min_sd = np.sqrt(min_variance)
    max_sd = np.sqrt(max_variance)

    return max(min_sd, min(sigma, max_sd))
