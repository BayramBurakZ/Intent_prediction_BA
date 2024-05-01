import numpy as np
import pandas as pd
from utilities.plots import *
from utilities.trajectory import *
from utilities.probability import *

path = r'trajectories\chosen_trajectories\test.csv'
df = pd.read_csv(path)

''' save pgs in csv later '''
pg1 = np.array([[0.8368], [0.2357], [0.1415]])
pg2 = np.array([[-0.8368], [0.2357], [0.1415]])
pg3 = np.array([[-0.8368], [-0.2357], [0.1415]])

goals = [pg1, pg2, pg3]
probability_goals = []  # accumulated probability of each goal

interval = 10
iterations = len(df) // interval


########################################################################################################


''' initial values '''
pp = np.array([[df['x'].iloc[0]], [df['y'].iloc[0]], [df['z'].iloc[0]]]) # position at t_n-2
p = np.array([[df['x'].iloc[interval]], [df['y'].iloc[interval]], [df['z'].iloc[interval]]]) # position at t_n-1
pn = np.array([[df['x'].iloc[2*interval]], [df['y'].iloc[2*interval]], [df['z'].iloc[interval]]]) # position at t_n

pp_t = df['time'].iloc[0]
p_t = df['time'].iloc[10]
pn_t = df['time'].iloc[20]


for i in range(min(3, iterations - 1)):

    # update observed positions
    if i > 0:
        pp = p
        p = pn
        pn = np.array([[df['x'].iloc[i + interval]], [df['y'].iloc[i + interval]], [df['z'].iloc[i + interval]]])
        pp_t = p_t
        p_t = pn_t
        pn_t = df['time'].iloc[i + interval]

    p_prime = normalize(position_derivative(pp, p, pp_t, p_t))  # derivative of points t_n-2, t_n-1
    pn_prime = normalize(position_derivative(p, pn, pp_t, p_t))  # derivative of points t_n-1, t_n

    print(p)
    print(pn)
    ''' save model trajectories and it's derivatives for each goal '''
    trajectories = []
    derivatives = []
    for g in goals:
        m = prediction_model_matrix(p, p_prime, g)
        trajectories.append(m[0])
        derivatives.append(m[1])

    ''' calculate points on trajectories and it's corresponding tangent vector '''
    path_points = []  # predicted points at the path
    tangential_vectors = []  # tangential vectors at path point
    for i in range(len(goals)):
        s = calculate_path_coordinate(p, pn, goals[i])
        path_points.append(calculate_polynomial(trajectories[i], s))
        tangential_vectors.append(normalize(calculate_polynomial(derivatives[i], s)))

    plot_3d_curve(trajectories, p, pn, pn_prime, goals, path_points, tangential_vectors)
    #plot_2d_curve(trajectories, p, pn, pn_prime, goals, path_points, tangential_vectors)

    ''' calculate the angles between the tangent pn_prime and all predicted tangents  '''
    angles = []
    for t in tangential_vectors:
        angles.append(calculate_angle(pn_prime, t))

    standard_deviation = np.std(angles)
    print(standard_deviation)

    plot_normal_distribution(standard_deviation)
    calculate_probability_angle(angles[0], standard_deviation)
    calculate_probability_angle(angles[1], standard_deviation)
    calculate_probability_angle(angles[2], standard_deviation)
