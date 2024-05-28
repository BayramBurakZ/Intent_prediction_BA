import numpy as np


class GoalManager:
    """ A class that manages all Goals """

    def __init__(self, goal_ids, active_goal_position, goals_probability, goals_sample_quantity, goal_threshold,
                 animated_plots, activate_plotter):
        """ Constructor for the GoalManager class

        :param goal_ids: (list) list of goal ids
        :param active_goal_position: (list)         list of active goal positions
        :param goals_probability: (list)            list of goals probability
        :param goals_sample_quantity: (list)        list of goals sample quantity
        :param goal_threshold: (float)              threshold for evaluating distant goal positions
        :param animated_plots: (AnimatedPlots)      instance for animating data
        :param activate_plotter: (bool)             activates the real time plotter
        """
        self.goal_ids = goal_ids
        # self.goals_closed_position
        self.goals_active_position = active_goal_position
        self.goals_probability = goals_probability
        self.goals_sample_quantity = goals_sample_quantity
        self.goal_threshold = goal_threshold  # TODO reconsider this approach

        self.animated_plots = animated_plots
        self.activate_plotter = activate_plotter

    def update_goals(self, t_current, p_current, action_db=None):
        """ Updates all goals and handles actions from database

        :param t_current: (NDArray[np.float64])    last measured time
        :param p_current: (NDArray[np.float64])    last measured point of the hand wrist
        :param action_db: (dataframe)               actions from database
        """
        # handle actions from db
        if action_db is not None:
            action_from = action_db['hand']
            action_tuple = (parse_action_string_to_tuples(action_db['action_id']))[0]
            print("received: ", action_tuple, "from: ", action_from)
            self.handle_action(action_tuple)

        print("time", t_current, " prob:", dec_to_per(self.goals_probability), "uncat:",
              self.uncategorized_goal_probability())

        # plot probabilities
        if self.activate_plotter:
            self.animated_plots.update_data(
                data_bar=[self.goal_ids, self.goals_probability, self.goals_sample_quantity,
                          distance_to_goals(self.goals_active_position, p_current),
                          self.uncategorized_goal_probability(), t_current])

    def handle_action(self, action):
        """ Handles action.
        :param action: (str)    action to be handled
        """
        if action[0] == 'pick':
            self.deactivate_goal(action[1])
        # TODO "other actions" ...

    def deactivate_goal(self, goal_id):
        """ Deactivate a goal.
        :param goal_id: (int)   goal id to be deactivated
        """
        assert goal_id in self.goal_ids, f"goal id {goal_id} not in goals"

        index = self.goal_ids.index(goal_id)

        # update the sizes of position, probability and sample quantity
        self.goal_ids.pop(index)
        self.goals_active_position.pop(index)
        self.goals_probability.pop(index)
        self.goals_sample_quantity.pop(index)

        print("removed id: ", goal_id)

    def activate_goal(self, goal_id):
        """ Activates a goal.

        :param goal_id: (int)   goal to be activated
        """
        # TODO implement when cleaned up database

        # self.goals_active_positions.insert(index, coordinates)
        # self.goals_probability.insert(index, 0)
        # self.goals_sample_quantity.insert(index, 0)

        print("activated goal 7")

    def uncategorized_goal_probability(self):
        """ Calculates the probability of no goal to be reached """
        return round(max(1 - sum(self.goals_probability), 0) * 100, 2)


def parse_action_string_to_tuples(action_string):
    """ Splits the action string from database into tuples

    :param action_string: (str)     action string
    :return: (tuple)                a tuple with action and goal id
    """
    components = action_string.split(',')
    result = []

    for component in components:
        parts = component.split('_')
        if len(parts) >= 2:
            # The first part is the action, the second part is the goal id
            action = parts[0]
            try:
                number = int(parts[1])
                result.append((action, number))
            except ValueError:
                print("corrupted database (other_)action")
                continue

    return result


def distance(v1, v2):
    """ Calculates the Euclidean distance between two vectors. """
    return np.linalg.norm(v1 - v2)


def dec_to_per(g):
    """ formats probability into percentage """
    return [round(x * 100, 2) for x in g]


def distance_to_goals(goals_active_positions, p_current):
    """ measures distance to goals"""
    d = []
    for g in goals_active_positions:
        d.append(distance(g, p_current))
    return d
