import numpy as np
import pandas
import pandas as pd

"""
ts_list = np.linspace(0, 1000, 100, dtype=int)
x_list = np.linspace(1, 0.2, 100)
y_list = np.linspace(0, 0.5, 100)
z_list = [1.0]*100"""




df = pd.DataFrame()

df['ID'] = [1,2,3,4]
df['x'] = [0.6,0.5,0.5,0.6]
df['y'] = [-0.4, -0.2,0.2, 0.4]
df['z'] = [1.0,1.0,1.0,1.0]

path = r'../data/goals/goal_test1.csv '
df.to_csv(path, index=False)