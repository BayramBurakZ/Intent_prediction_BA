import pandas as pd
from utilities.plots import *
from utilities.trajectory import *

path = r'trajectories\chosen_trajectories\test.csv'
df = pd.read_csv(path)

# testing values
pg1 = np.array([[20.8309], [10.2293], [0.1475]])
pg2 = np.array([[0.8309], [-0.2293], [0.1475]])
pg3 = np.array([[10.8309], [-10.2293], [0.1475]])

pp = np.array([[df['x'].iloc[0]], [df['y'].iloc[0]], [df['z'].iloc[0]]])
p = np.array([[df['x'].iloc[4]], [df['y'].iloc[4]], [df['z'].iloc[4]]])
pn = np.array([[df['x'].iloc[22]], [df['y'].iloc[22]], [df['z'].iloc[2]]])

p_t = df['time'].iloc[0]
pn_t = df['time'].iloc[4]
pn2_t = df['time'].iloc[22]

#goals = (pg1, pg2, pg3)
goals = []
goals.append(pg1)
########################################################################################################


p_prime = normalize(position_derivative(pp, p, p_t, pn_t))
pn_prime = normalize(position_derivative(p, pn, p_t, pn_t))

M = []
for g in goals:
    M.append(prediction_model_matrix(p, p_prime, g))

trajectories = []
for m in M:
    trajectories.append(m[0])

derivatives = []
for m in M:
    derivatives.append(m[1])

path_points = []
tangential_vectors = []
for i in range(len(goals)):
    s = calculate_path_coordinate(p, pn, goals[i])
    path_points.append(calculate_polynomial(trajectories[i], s))
    tangential_vectors.append(normalize(calculate_polynomial(derivatives[i], s)))

draw_3d_curve(trajectories, p, pn, pn_prime, goals, path_points, tangential_vectors)
