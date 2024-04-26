import pandas as pd
from utilities.plots import *
from utilities.trajectory import *

path = r'trajectories\chosen_trajectories\test.csv'
df = pd.read_csv(path)

df = df.iloc[14:]
df = df[:-1]

# testing values
pg1 = np.array([[10.0], [10.0], [10.0]])
pg2 = np.array([[-30.7200], [5.008306], [1.1195]])
p = np.array([[205858], [0], [0], [0]])
pn = np.array([[205876], [0.7016], [-0.1288], [0.03467]])


p_prime = position_velocity(p, pn)
p1 = np.delete(p, 0, 0)

M1 = prediction_model_matrix(0.4, p1, p_prime, pg1)
M2 = prediction_model_matrix(0.4,p1,p_prime, pg2)
draw_3d_curve(M1, M2, p1, p_prime, pg1, pg2)