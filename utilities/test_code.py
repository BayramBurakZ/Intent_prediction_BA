# Coordinates of goals || Array numbered according to Blender objects
'''
goals_study = [[np.nan, np.nan],[np.nan, np.nan],[0.2,-0.4,0.03],[0.3, -0.4,0.03],[0.4, -0.4,0.03],[0.5, -0.4,0.03],[0.6, -0.4,0.03], # white long
         [0.2,-0.3,0.03],[0.3,-0.3,0.03],[0.4,-0.3,0.03],[0.5,-0.3,0.03],[0.6,-0.3,0.03],[0.3,-0.2,0.03],[0.4,-0.2,0.03],[0.5,-0.2,0.03],[0.6,-0.2,0.03], # white short
         [0.3, 0.2,0.03],[0.4,0.2,0.03],[0.5,0.2,0.03],[0.6,0.2,0.03], # red short
         [0.2,0.3,0.03],[0.2,0.3,0.03],[0.2,0.4,0.03], # red long
         [0.3,0.3,0.03],[0.4,0.3,0.03],[0.5,0.3,0.03],[0.6,0.3,0.03], # short green
         [0.3, 0.4,0.03],[0.4,0.4,0.03],[0.5,0.4,0.03],[0.6,0.4,0.03], # short purple
         [0.3,0.5,0.03],[0.3,0.5,0.03],[0.3,0.5,0.03]] # short blue

         # Dataframe for goals
data = {'ID': list(range(3, 35)),
        'x': [0.2, 0.3, 0.4, 0.5, 0.6, 0.2, 0.3, 0.4, 0.5, 0.6, 0.3, 0.4, 0.5, 0.6, 0.3, 0.4, 0.5, 0.6, 0.2, 0.2, 0.2,
              0.3, 0.4, 0.5, 0.6, 0.3, 0.4, 0.5, 0.6, 0.3, 0.3, 0.3],
        'y': [-0.4, -0.4, -0.4, -0.4, -0.4, -0.3, -0.3, -0.3, -0.3, -0.3, -0.2, -0.2, -0.2, -0.2, 0.2, 0.2, 0.2, 0.2,
              0.3, 0.3, 0.4, 0.3, 0.3, 0.3, 0.3, 0.4, 0.4, 0.4, 0.4, 0.5, 0.5, 0.5],
        'z': [0.03] * 32,
        'active': [True] * 32,
        'sample': [0] * 32,
        'probability': [0] * 32,
        }

'''


import numpy as np
import pandas as pd
from utilities.plots import *
from utilities.trajectory import *
from utilities.probability import *


path = r'data_csv\chosen_trajectories\test.csv'
#path = r'data_csv\left_hand\left_9.csv'
df = pd.read_csv(path)

''' save pgs in csv later '''
pg1 = np.array([[0.8368], [0.2357], [0.1415]])
pg2 = np.array([[-0.8368], [0.2357], [0.3415]])
pg3 = np.array([[-0.8368], [-0.2357], [-0.1415]])
pg4 = np.array([[-1.8368], [-0.2357], [0.1415]])
pg5 = np.array([[2.8368], [-0.2357], [0.1415]])


goals = [pg1, pg2,pg3]
probability_goals = []  # accumulated probability of each goal

interval = 10
max_iterations = len(df) // interval
iterations = 3

########################################################################################################


''' initial values '''
pp = np.array([[df['x'].iloc[0]], [df['y'].iloc[0]], [df['z'].iloc[0]]])  # position at t_n-2
p = np.array([[df['x'].iloc[interval]], [df['y'].iloc[interval]], [df['z'].iloc[interval]]])  # position at t_n-1
pn = np.array([[df['x'].iloc[2 * interval]], [df['y'].iloc[2 * interval]], [df['z'].iloc[interval]]])  # position at t_n

pp_t = df['time'].iloc[0]
p_t = df['time'].iloc[10]
pn_t = df['time'].iloc[20]

p_prime = position_derivative(pp, p)  # derivative of points t_n-2, t_n-1
pn_prime = position_derivative(p, pn)  # derivative of points t_n-1, t_n

for i in range(min(iterations, max_iterations - 1)):

    # update observed positions
    if i > 0:
        pp = p
        p = pn
        pn = np.array([[df['x'].iloc[i + interval]], [df['y'].iloc[i + interval]], [df['z'].iloc[i + interval]]])

        pp_t = p_t
        p_t = pn_t
        pn_t = df['time'].iloc[i + interval]

        p_prime = pn_prime
        pn_prime = position_derivative(p, pn)  # derivative of points t_n-1, t_n

        print(p, pn, p_prime, pn_prime)


    ''' save model data_csv and it's derivatives for each goal '''
    trajectories = []
    derivatives = []
    for g in goals:
        m = prediction_model_matrix(p, p_prime, g)
        trajectories.append(m[0])
        derivatives.append(m[1])

    ''' calculate points on data_csv and it's corresponding tangent vector '''
    path_points = []  # predicted points at the path
    tangential_vectors = []  # tangential vectors at path point
    for j in range(len(goals)):
        s = calculate_path_coordinate(p, pn, goals[j])
        path_points.append(calculate_polynomial(trajectories[j], s))
        tangential_vectors.append(normalize(calculate_polynomial(derivatives[j], s)))

    #plot_3d_curve(data_csv, p, pn, pn_prime, goals, path_points, tangential_vectors)
    plot_2d_curve(trajectories, p, pn, pn_prime, goals, path_points, tangential_vectors)

    ''' calculate the angles between the tangent pn_prime and all predicted tangents  '''
    angles = []
    for t in tangential_vectors:
        angles.append(calculate_angle(pn_prime, t))

    variance = calculate_variance(angles)