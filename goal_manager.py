class GoalManager:
    def __init__(self, df, active_goal_positions, goals_probability, goals_sample_quantity, goal_threshold):
        self.df = initialize_df(df)
        self.active_goal_positions = active_goal_positions
        self.goals_probability = goals_probability
        self.goals_sample_quantity = goals_sample_quantity
        self.goal_threshold = goal_threshold

    def update_goals(self):
        return  # print(tr(self.goals_probability))

    def uncategorized_goal_probability(self):
        return max(1, 1 - self.df['probability'].sum())

    def activate_goal(self, goal_id):
        assert not self.df.loc[['ID'] == goal_id, 'active'], "goal already activated"
        self.df.loc[['ID'] == goal_id, 'active'] = True
        coordinates = self.id_to_coordinates(goal_id)

        active_goals = self.get_all_active_goals()
        next_id = self.df[self.df['ID'] > goal_id]['ID'].min()
        index = self.df[self.df['ID'] == next_id].index[0]
    def deactivate_goal(self, goal_id):
        print(self.df)
        print(self.active_goal_positions)
        coordinates = self.id_to_coordinates(goal_id)
        goal_position = [v.flatten().tolist() for v in self.active_goal_positions]
        print(coordinates)
        print(goal_position)

        index = goal_position.index([coordinates[0], coordinates[1], coordinates[2]])
        print(index)
        if index in self.active_goal_positions:
            self.active_goal_positions.remove(index)
        self.df.loc[['ID'] == goal_id, 'active'] = False


        print("removed id: ", goal_id)
        print(self.df)
        print(self.active_goal_positions)

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
