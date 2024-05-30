import numpy as np
import pandas
import pandas as pd







df = pd.DataFrame()


ts_list = np.linspace(0, 1000, 588, dtype=int)
#z1_list = [1.0]*588


x1_list = np.linspace(1, 0.5, 147)
y1_list = np.linspace(0, -1.0, 147)

x2_list = np.linspace(0.5, 0, 147)
y2_list = np.linspace(-1.0, 0.0, 147)

x3_list = np.linspace(0.0, 1.0, 147)
y3_list = np.linspace(0.0, 0.0, 147)

x4_list = np.linspace(1.0, 0.0, 147)
y4_list = np.linspace(0.0, 1.0, 147)


df['time'] = ts_list
df['x'] = [*x1_list, *x2_list, *x3_list, *x4_list]
df['y'] = [*y1_list, *y2_list, *y3_list, *y4_list]
df['z'] = [1.0]*588
"""df['ID'] = [1,2,3,4]
df['x'] = [0.6,0.5,0.5,0.6]
df['y'] = [-0.4, -0.2,0.2, 0.4]
df['z'] = [1.0,1.0,1.0,1.0]"""

#path = r'../data/goals/goal_test2.csv '

path = r'../data/test_trajectories/traj_test3.csv'
df.to_csv(path, index=False)