import numpy as np
from scipy import stats


class ProbabilityEvaluator:
    """ A class that evaluates the probability of each goal.

        Attributes:
            sample_size_of_goals: (list)        amount of sample for accumulated probability
            probability_goals: (list)           probability of each goal
            probability_uncategorized: (float)  probability of no goal
    """

    def __init__(self, number_of_goals):
        """ Initializes the probability evaluator.

            :param number_of_goals: (int)   amount of goals
        """
        self.number_of_goals = number_of_goals
        self.sample_size_of_goals = [0] * number_of_goals
        self.probability_goals = [0] * number_of_goals
        self.probability_uncategorized = 0

    def evaluate_angles(self, dp_current, direction_vectors):
        """ Evaluates the angles between predicted and measured directional vector.

        :param dp_current: (NDArray[np.float64])                current directional vector
        :param direction_vectors: (List[NDArray[np.float64]])   predicted directional vectors
        """
        angles = []
        for dv in direction_vectors:
            angles.append(calculate_angle(dp_current, dv))

        sd_of_angles = calculate_standard_deviation(angles)

        for i in range(self.number_of_goals):
            # probability of last measured angle
            probability_angle = calculate_probability_angle(angles[i], sd_of_angles)
            # accumulated probability over n samples
            self.probability_goals[i] = calculate_probability_goal(self.probability_goals[i], probability_angle)

            # update the sample size
            if self.probability_goals[i] == 0:
                self.sample_size_of_goals[i] = 0  # reset sample size along with goal probability
            else:
                self.sample_size_of_goals[i] += 1

        # normalize probability of goals
        norm_divisor = probability_normalization_divisor(self.probability_goals)
        self.probability_goals = [x / norm_divisor for x in self.probability_goals]
        self.probability_uncategorized = probability_uncategorized_goal(self.probability_goals)


def calculate_angle(v1, v2):
    """ Calculates the angle on x,y plane between two vectors. """
    if v1.shape[0] != 2:
        # remove z
        v1 = v1[:2]

    if v2.shape[0] != 2:
        # remove z
        v2 = v2[:2]

    v1 = np.squeeze(v1)
    v2 = np.squeeze(v2)

    # normalize
    v1_norm = np.linalg.norm(v1)
    v2_norm = np.linalg.norm(v2)

    if not np.isclose(v1_norm, 1, 0.0001) or not np.isclose(v2_norm, 1, 0.0001):
        return np.pi

    # calculate angle
    dot = np.dot(v1, v2)
    cos_angle = dot / (v1_norm * v2_norm)

    return np.arccos(cos_angle)  # in radiance


def calculate_standard_deviation(angles):
    """ Calculates the standard deviation of angles.

    :param angles: (list)   angles as samples
    :return: (float)        standard deviation
    """
    sigma = np.std(angles)

    # boundaries for standard deviation
    min_sd = np.sqrt(1 / 8)
    max_sd = np.sqrt(1 / 16)

    if sigma < min_sd:
        sigma = min_sd

    if sigma > max_sd:
        sigma = max_sd

    return sigma


def calculate_probability_angle(angle, sigma, mu=0):
    """ Calculates the probability of an angle using the PDF function on a normal distribution.

    :param angle: (float)   angle to be evaluated
    :param sigma: (float)   standard deviation
    :param mu: (float)      mean

    :return: (float)    probability of the angle
    """
    return stats.norm.pdf(angle, mu, sigma)


def calculate_probability_goal(cumulative_probability, angle_probability):
    """ Calculates the cumulative probability of a goal.

    :param cumulative_probability: (float)  accumulated probability over samples
    :param angle_probability: (float)       probability of each angle

    :return: (float)                        cumulative probability over samples
    """
    # TODO: bug where some probabilities are nan. consider max boundary as well
    # lower boundary
    min_probability = 0.01

    # reset cumulated probability ( sample n = 0 )
    if angle_probability < min_probability:
        return 0

    if cumulative_probability < min_probability:
        return angle_probability  # first probability ( sample n = 1 )
    else:
        return cumulative_probability * angle_probability  # update probability ( sample n = n+1 )


def probability_normalization_divisor(probability_all_goals):
    """ Calculates the normalization divisor for all goals.

    :param probability_all_goals: (list)   probability of each goal
    :return: (float) normalization divisor
    """
    return max(1, sum(probability_all_goals))


def probability_uncategorized_goal(normalized_probability_all_goals):
    """ Calculates the probability of an uncategorized goal.

    :param normalized_probability_all_goals: (List[float])  normalized probability of each goal
    :return: (float) probability of uncategorized goal
    """
    return min(0, 1 - sum(normalized_probability_all_goals))
