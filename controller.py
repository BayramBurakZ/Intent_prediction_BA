import sys

from goal_manager import *
from prediction_model import PredictionModel
from probability_evaluator import ProbabilityEvaluator


class Controller:
    """ A class that controls the flow of data.

    Attributes:
        sample_min_distance: (float)                        minimum distance between samples to calculate prediction
        prediction_model: (PredictionModel)             the prediction model
        probability_evaluator: (ProbabilityEvaluator)   the probability evaluator

    """

    def __init__(self, df, goal_threshold, sample_min_distance, min_variance, max_variance):
        """ Initializes the DataProcessor object.

        :param all_goal_positions: (List[NDArray[np.float64]])  coordinates of all goals
        :param sample_min_distance: (float)     minimum distance between samples to calculate prediction
        """
        self.active_goal_positions = df_process_goal_positions(df)
        self.goals_probability = [0] * len(self.active_goal_positions)
        self.goals_sample_quantity = [0] * len(self.active_goal_positions)

        self.prediction_model = PredictionModel(sample_min_distance)
        self.probability_evaluator = ProbabilityEvaluator(self.goals_probability, self.goals_sample_quantity,
                                                          min_variance, max_variance)
        self.goal_manager = GoalManager(df, self.active_goal_positions, self.goals_probability,
                                        self.goals_sample_quantity, goal_threshold)



    def process_data(self, data):
        """ Processes the incoming data.

        :param data: (List[int, NDArray[np.float64]])  data to be processed
        """

        if is_bad_data(data):
            print("skipped bad data")
            return

        t_current = data[0]
        p_current = data[1]

        direction_vectors = self.prediction_model.calculate_predicted_direction(p_current, self.active_goal_positions)

        if direction_vectors is not None:
            self.probability_evaluator.evaluate_angles(self.prediction_model.dp_current, direction_vectors)

            if len(data) > 2:
                actions = data[2]
                self.goal_manager.update_goals(p_current, t_current, actions)
                print(f"time: {data[0]},  {tra(self.goals_probability)}")
            else:
                self.goal_manager.update_goals(p_current, t_current)
                print(f"time: {data[0]},  {tra(self.goals_probability)}")


            """
            try:
                # Check for termination condition
                user_input = input("Do you want to exit the program? (y/n): ")
                if user_input.lower() == "y":
                    sys.exit()

                # Continue with other operations

            except Exception as e:
                print(f"An error occurred: {e}")
                sys.exit()"""


def tra(g):
    return [round(x * 100, 2) for x in g]


def is_bad_data(data):
    """ checks for bad data """
    if data[0] < 0 or not isinstance(data[0], int):
        return True

    # TODO: catch bad coordinates earlier!
    """
    if all(not isinstance(item, float) for item in data[1].flatten().tolist()):
        return True"""

    return False


def df_process_goal_positions(df):
    goal_positions = []
    for index, row in df.iterrows():
        goal_positions.append([row['x'], row['y'], row['z']])

    assert len(goal_positions) > 0, "the list of goal can not be empty"
    # assert all(goal.shape == (3, 1) for goal in goal_positions), "goal vectors must have the shape (3,1) "

    return goal_positions
