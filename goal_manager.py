import numpy as np

class GoalManager:
    def __init__(self, df, active_goal_positions, goals_probability, goals_sample_quantity, goal_threshold):
        self.df = initialize_df(df)
        self.goals_active_positions = active_goal_positions
        self.goals_probability = goals_probability
        self.goals_sample_quantity = goals_sample_quantity
        self.goal_threshold = goal_threshold

    def update_goals(self, p_current, t_current, actions = None):
        if actions is not None:
            print(actions)

        return  # print(tr(self.goals_probability))

    def activation_radius(self, p_current):
        #TODO: change this with blind spot function
        for index, row in self.df.iterrows():
            coordinates = np.array([row['x'], row['y'], row['z']])
            goal_id = row['ID']

            print(distance(coordinates, p_current))
            if row['active'] and distance(coordinates, p_current) >  self.goal_threshold:
                self.deactivate_goal(goal_id)

            if not row['active'] and distance(coordinates, p_current) <  self.goal_threshold:
                self.activate_goal(goal_id)


    def uncategorized_goal_probability(self):
        return max(1, 1 - self.df['probability'].sum())

    def activate_goal(self, goal_id):

        try:
            assert goal_id in self.df['ID'].values, f"goal id {goal_id} not in goals"
            assert not self.df.loc[self.df['ID'] == goal_id, 'active'].values[0], f"goal id {goal_id} already activated"
        except AssertionError as e:
            print(e)
            return

        self.df.loc[self.df['ID'] == goal_id, 'active'] = True
        coordinates = self.id_to_coordinates(goal_id)

        next_id = self.df[self.df['ID'] > goal_id]['ID'].min()
        index = self.df[self.df['ID'] == next_id].index[0]

        self.goals_active_positions.insert(index, coordinates)
        self.goals_probability.insert(index, 0)
        self.goals_sample_quantity.insert(index, 0)

        print("activated goal 7")

    def deactivate_goal(self, goal_id):

        try:
            assert goal_id in self.df['ID'].values, f"goal id {goal_id} not in goals"
            assert self.df.loc[self.df['ID'] == goal_id, 'active'].values[0], f"goal id {goal_id} already deactivated"
        except AssertionError as e:
            print(e)
            return

        coordinates = self.id_to_coordinates(goal_id)
        index = self.goals_active_positions.index([coordinates[0], coordinates[1], coordinates[2]])

        self.goals_active_positions.pop(index)
        self.goals_probability.pop(index)
        self.goals_sample_quantity.pop(index)

        self.df.loc[self.df['ID'] == goal_id, 'active'] = False

        print("removed id: ", goal_id)

    def get_all_active_goals(self):
        return self.df.loc[self.df['active']].sort_values(by='ID')

    def id_to_coordinates(self, goal_id):
        coordinates = self.df.loc[self.df['ID'] == goal_id, ['x', 'y', 'z']].values.tolist()
        return coordinates[0]


def tr(g):
    return [round(x * 100, 2) for x in g]


def initialize_df(df):
    df['active'] = True
    df['sample'] = 0
    df['probability'] = 0
    return df

def distance(v1, v2):
    """ Calculates the Euclidean distance between two vectors. """
    return np.linalg.norm(v1 - v2)