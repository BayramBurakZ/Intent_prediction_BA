import numpy as np
from scipy import stats


class ProbabilityEvaluator:
    """ A class that evaluates the probability of each goal.

        Attributes:
            goals_sample_quantity: (list)                amount of sample for accumulated probability
            goals_probability: (list)           probability of each goal
    """

    def __init__(self, goals_probability, goals_sample_quantity, min_variance, max_variance):
        """ Initializes the probability evaluator.

            :param sample_sizes: (list)                amount of sample for accumulated probability
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
        for dv in direction_vectors:
            angles.append(calculate_angle(dp_current, dv))

        sd_of_angles = calculate_standard_deviation(angles, self.min_variance, self.max_variance)

        for i in range(goal_amount):
            # probability of last measured angle
            probability_angle = calculate_probability_angle(angles[i], sd_of_angles)
            # accumulated probability over n samples
            self.goals_probability[i] = calculate_probability_goal(self.goals_probability[i], probability_angle)

            # update the sample size
            if np.isclose(self.goals_probability[i], 0, 0.001):
                self.goals_sample_quantity[i] = 0  # reset sample size along with goal probability
            else:
                self.goals_sample_quantity[i] += 1

        # normalize probability of goals
        norm_divisor = probability_normalization_divisor(self.goals_probability)
        for i in range(goal_amount):
            self.goals_probability[i] /= norm_divisor


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

    if np.isclose(v1_norm, 0, 0.001) or np.isclose(v2_norm, 0, 0.001):
        return np.pi

    # calculate angle
    dot = np.dot(v1, v2)
    cos_angle = dot / (v1_norm * v2_norm)

    return np.arccos(cos_angle)  # in radiance


def calculate_standard_deviation(angles, min_variance, max_variance):
    """ Calculates the standard deviation of angles.

    :param angles: (list)   angles of predicted direction vector
    :return: (float)        standard deviation
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
    return 1 - min(1, sum(normalized_probability_all_goals))
