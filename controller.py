from goal_manager import GoalManager
from prediction_model import PredictionModel
from probability_evaluator import ProbabilityEvaluator
from real_time_plotter import AnimatedPlots


class Controller:
    """ A class that controls the flow of data.

    Attributes:
        goals_position: (List)                          list of goal positions
        goals_probability: (list)                       list of goals probability
        goals_sample_quantity: (list)                   list of goals sample quantity
        animated_plots: (AnimatedPlots)                 instance for animating data
        goal_manager: (GoalManager)                     instance for manipulating the goal
        prediction_model: (PredictionModel)             instance for calculating trajectories
        probability_evaluator: (ProbabilityEvaluator)   instance for evaluating probability
    """

    def __init__(self, df, goal_threshold, sample_min_distance, min_variance, max_variance, activate_plotter):
        """ Constructor for the Controller class.

        :param df: (dataframe)                      dataframe with goal positions and goal id
        :param goal_threshold: (float)              threshold for evaluating distant goal positions
        :param sample_min_distance: (float)         min distant to start modelling trajectories
        :param min_variance: (float)                lower limit for variance in normal distribution
        :param max_variance: (float)                upper limit for variance in normal distribution
        :param activate_plotter: (bool)             activates the real time plotter
        """
        self.goals_position = df_process_goal_positions(df)
        self.goals_probability = [0] * len(self.goals_position)
        self.goals_sample_quantity = [0] * len(self.goals_position)

        # live visualization with real time plotter (optional) #TODO massive performance problems when plotting
        if activate_plotter:
            self.animated_plots = AnimatedPlots(self.goals_position)
            self.animated_plots.animate()

        self.goal_manager = GoalManager(df['ID'].tolist(), self.goals_position, self.goals_probability,
                                        self.goals_sample_quantity, goal_threshold, self.animated_plots,
                                        activate_plotter)

        self.prediction_model = PredictionModel(sample_min_distance, self.animated_plots, activate_plotter)
        self.probability_evaluator = ProbabilityEvaluator(self.goals_probability, self.goals_sample_quantity,
                                                          min_variance, max_variance)

    def process_data(self, data):
        """ Distributes incoming data. Data contains [0]-> time, [1]-> hand wrist position
            and [2] -> actions from database.

        :param data: (List[int, NDArray[np.float64], Dataframe)     data to be processed
        """
        # TODO: catch bad data

        # calculate predicted direction
        direction_vectors = self.prediction_model.calculate_predicted_direction(data[1], self.goals_position)

        if direction_vectors is not None:
            # calculate the probability of predicted direction
            self.probability_evaluator.evaluate_angles(self.prediction_model.dp_current, direction_vectors)
        else:
            print("skipped at: " + str(data[0]))

        if len(data) > 2:  # update goals
            self.goal_manager.update_goals(data[0], data[1], data[2])
        else:
            self.goal_manager.update_goals(data[0], data[1])


def df_process_goal_positions(df):
    """ Processes data frame of goal coordinates.

    :param df: (dataframe)      goal position dataframe with ids
    :return: (list)             list of goal coordinates
    """
    goal_positions = []
    for index, row in df.iterrows():
        goal_positions.append([row['x'], row['y'], row['z']])

    assert len(goal_positions) > 0, "the list of goal can not be empty"

    return goal_positions
