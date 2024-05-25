import numpy as np
import pandas as pd

from probability_evaluation import ProbabilityEvaluator
from utilities.plots import *
#from utilities.trajectory import *
from utilities.probability import *
from prediction_model import *

#path = r'data_csv\chosen_trajectories\test.csv'
path = r'data_csv\left_hand\left_9.csv'
df = pd.read_csv(path)

''' save pgs in csv later '''
pg1 = np.array([[0.8368], [0.2357], [0.1415]])
pg2 = np.array([[-0.8368], [0.2357], [0.3415]])
pg3 = np.array([[-0.8368], [-0.2357], [-0.1415]])
pg4 = np.array([[-1.8368], [-0.2357], [0.1415]])
pg5 = np.array([[2.8368], [-0.2357], [0.1415]])

goals = [pg1, pg2, pg3]
probability_goals = []  # accumulated probability of each goal

interval = 50
max_iterations = len(df) // interval
iterations = 10

########################################################################################################


''' initial values '''
pp = np.array([[df['x'].iloc[0]], [df['y'].iloc[0]], [df['z'].iloc[0]]])  # position at t_n-2
p = np.array([[df['x'].iloc[interval]], [df['y'].iloc[interval]], [df['z'].iloc[interval]]])  # position at t_n-1
pn = np.array([[df['x'].iloc[2 * interval]], [df['y'].iloc[2 * interval]], [df['z'].iloc[interval]]])  # position at t_n

pp_t = df['time'].iloc[0]
p_t = df['time'].iloc[10]
pn_t = df['time'].iloc[20]

prediction_model = PredictionModel(goals)
probability_evaluator = ProbabilityEvaluator(len(goals))

for i in range(min(iterations, max_iterations - 1)):

    if i > 0:
        pn = np.array([[df['x'].iloc[i + interval]], [df['y'].iloc[i + interval]], [df['z'].iloc[i + interval]]])
        pn_t = df['time'].iloc[i + interval]

    direction_vectors = prediction_model.calculate_predicted_angles(pn, pn_t)
    probability_evaluator.evaluate_angles(prediction_model.dp_current, direction_vectors)

    print(probability_evaluator.probability_goals)
    print(probability_evaluator.sample_size_of_goals)

