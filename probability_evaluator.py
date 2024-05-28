import numpy as np
from scipy import stats


class ProbabilityEvaluator:
    """ A class that evaluates the probability of each goal.

        Attributes:
            goals_probability: (list)       probability of each goal
            goals_sample_quantity: (list)   amount of sample for accumulated probability
    """

    def __init__(self, goals_probability, goals_sample_quantity, min_variance, max_variance):
        """ Constructor for the ProbabilityEvaluator class.

        :param goals_probability: (list)        list of goals probability
        :param goals_sample_quantity: (list)    list of goals sample quantity
        :param min_variance: (float)            lower limit for variance in normal distribution
        :param max_variance: (float)            upper limit for variance in normal distribution
        """
        self.goals_probability = goals_probability
        self.goals_sample_quantity = goals_sample_quantity

        self.min_variance = min_variance
        self.max_variance = max_variance

    def evaluate_angles(self, dp_current, direction_vectors):
        """ Evaluates the angles between predicted and measured directional vector.

        :param dp_current: (NDArray[np.float64])                current directional vector
        :param direction_vectors: (List[NDArray[np.float64]])   predicted directional vectors
        """
        goal_amount = len(direction_vectors)
        angles = []
        # calculate angles between measured direction and predicted directions
        for dv in direction_vectors:
            angles.append(calculate_angle(dp_current, dv))

        # calculates standard deviation of all angles
        sd_of_angles = calculate_standard_deviation(angles, self.min_variance, self.max_variance)

        for i in range(goal_amount):
            # probability an angle
            angle_probability = stats.norm.pdf(angles[i], 0, sd_of_angles)
            # accumulated probability over n samples
            self.goals_probability[i] = calculate_probability_goal(self.goals_probability[i], angle_probability)

            # update the sample size
            if np.isclose(self.goals_probability[i], 0, 0.001):
                self.goals_sample_quantity[i] = 0  # reset sample size along with goal probability
            else:
                self.goals_sample_quantity[i] += 1

        # normalize probability of goals
        norm_divisor = max(1, sum(self.goals_probability))
        for i in range(goal_amount):
            self.goals_probability[i] /= norm_divisor


def calculate_angle(v1, v2):
    """ Calculates the angle on x,y plane between two 3D vectors. """

    # remove z component
    v1 = v1[:2]
    v2 = v2[:2]

    # normalize
    v1_norm = np.linalg.norm(v1)
    v2_norm = np.linalg.norm(v2)

    if np.isclose(v1_norm, 0, 0.001) or np.isclose(v2_norm, 0, 0.001):
        return np.pi

    # calculate angle
    dot = np.dot(v1, v2)
    cos_angle = dot / (v1_norm * v2_norm)

    return np.arccos(cos_angle)  # in radiance


def calculate_standard_deviation(angles, min_variance, max_variance):
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

    if sigma < min_sd:
        sigma = min_sd

    if sigma > max_sd:
        sigma = max_sd

    return sigma


def calculate_probability_goal(cumulative_probability, angle_probability):
    """ Calculates the cumulative probability of a goal.

    :param cumulative_probability: (float)  accumulated probability over samples
    :param angle_probability: (float)       probability of each angle

    :return: (float)                        cumulative probability over samples
    """
    # lower boundary for probability
    min_probability = 0.001

    # reset cumulated probability ( sample n = 0 )
    if angle_probability < min_probability:
        return 0

    if cumulative_probability < min_probability:
        return angle_probability  # first probability ( sample n = 1 )
    else:
        return cumulative_probability * angle_probability  # update probability ( sample n = n+1 )
