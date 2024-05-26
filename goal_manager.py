import pandas as pd


class GoalManager:
    def __init__(self, df, active_goal_positions, goals_probability, goals_sample_quantity, goal_threshold):
        self.df = initialize_df(df)
        self.active_goal_positions = active_goal_positions
        self.goals_probability = goals_probability
        self.goals_sample_quantity = goals_sample_quantity
        self.goal_threshold = goal_threshold

    def update_goals(self):
        return #print(tr(self.goals_probability))
    def uncategorized_goal_probability(self):
        return max(1, 1 - self.df['probability'].sum())

def tr(g):
    return [round(x * 100, 2) for x in g]
def initialize_df(df):
    df['active'] = True
    df['sample'] = 0
    df['probability'] = 0
    return df
