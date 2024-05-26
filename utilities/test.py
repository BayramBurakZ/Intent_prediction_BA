
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
    return 1 - sum(normalized_probability_all_goals)