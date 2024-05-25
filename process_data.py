from prediction_model import PredictionModel
from probability_evaluator import ProbabilityEvaluator

import pandas as pd
import numpy as np
from numpy.typing import NDArray
from typing import List


class DataProcessor:

    def __init__(self, coordinates: List[NDArray[np.float64]], sample_distance=0.05):
        self.sample_distance = sample_distance
        self.prediction_model = PredictionModel(coordinates)
        self.probability_evaluator = ProbabilityEvaluator(len(coordinates))

    def process_data(self, data):
        p_previous = self.prediction_model.p_previous
        p_current = data[1]
        t_current = data[0]

        # only calculate equidistant measurements
        if euclidean_distance(p_previous, p_current) < self.sample_distance:
            return

        direction_vectors = self.prediction_model.calculate_predicted_angles(p_current, t_current)
        self.probability_evaluator.evaluate_angles(self.prediction_model.dp_current, direction_vectors)
        print(f"p: {data[0]}, Timestamp: {data[1]}, probability: {self.probability_evaluator.probability_goals}")


def euclidean_distance(column_vector1, column_vector2):
    if column_vector1.shape != (3, 1) or column_vector2.shape != (3, 1):
        raise ValueError("Vectors must have the shape (3,1).")

    return np.linalg.norm(column_vector1 - column_vector2)