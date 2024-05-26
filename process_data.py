import numpy as np

from prediction_model import PredictionModel
from probability_evaluator import ProbabilityEvaluator


class DataProcessor:
    """ A class that processes the incoming data.

    Attributes:
        sample_distance: (float)                        minimum distance between samples to calculate prediction
        prediction_model: (PredictionModel)             the prediction model
        probability_evaluator: (ProbabilityEvaluator)   the probability evaluator

    """

    def __init__(self, all_goal_positions, sample_distance=0.15):
        """ Initializes the DataProcessor object.

        :param all_goal_positions: (List[NDArray[np.float64]])  coordinates of all goals
        :param sample_distance: (float)     minimum distance between samples to calculate prediction
        """
        assert len(all_goal_positions) > 0, "the list of goal can not be empty"
        assert all(goal.shape == (3, 1) for goal in all_goal_positions), "goal vectors must have the shape (3,1) "

        self.sample_distance = sample_distance
        self.prediction_model = PredictionModel(all_goal_positions)
        self.probability_evaluator = ProbabilityEvaluator(len(all_goal_positions))

    def process_data(self, data):
        """ Processes the incoming data.

        :param data: (List[int, NDArray[np.float64]])  data to be processed
        """
        if is_bad_data(data):
            return

        t_current = data[0]
        p_current = data[1]
        p_previous = self.prediction_model.p_current

        # only calculate after minimum distance between measurements is reached
        if euclidean_distance(p_previous, p_current) < self.sample_distance:
            return

        direction_vectors = self.prediction_model.calculate_predicted_direction(p_current, t_current)
        self.probability_evaluator.evaluate_angles(self.prediction_model.dp_current, direction_vectors)
        print(
            f"p: {data[0]}, Timestamp: {data[1]}, probability: {self.probability_evaluator.probability_goals, self.probability_evaluator.probability_uncategorized}")


def euclidean_distance(column_vector1, column_vector2):
    """ Calculates the Euclidean distance between two vectors. """
    return np.linalg.norm(column_vector1 - column_vector2)


def is_bad_data(data):
    """ checks for bad data """
    if data[0] < 0 or not isinstance(data[0], int):
        return True

    # TODO: catch bad coordinates earlier!
    """
    if all(not isinstance(item, float) for item in data[1].flatten().tolist()):
        return True"""

    return False
