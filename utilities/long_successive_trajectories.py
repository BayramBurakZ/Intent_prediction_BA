import pandas as pd

#path = r'trajectories\left_hand\left_10.csv'
path = r'../trajectories/right_hand/right_9.csv'

df = pd.read_csv(path)
# new column 'increasing', True if the following line is greater
df['increasing'] = (df['time'].diff() > 0) & (df['x'].diff() > 0) & (df['y'].diff() > 0)

# new column 'group' to save the largest chains
df['group'] = (df['increasing'] != df['increasing'].shift()).cumsum()

# filter all true values
df_increasing = df[df['increasing']]

# count number of data in a group and sort it
group_counts = df_increasing['group'].value_counts().sort_values(ascending=False)

# get the 10 longest trajectories
top_10_groups = group_counts.head(1).index

# df with only 10 longest trajectories
df_top_10 = df_increasing[df_increasing['group'].isin(top_10_groups)]

'''
# get the difference between first and last x value in a group
df_top_10['dX'] = df_top_10.groupby('group')['x'].transform(lambda x: x.max() - x.min())
df_top_10['dY'] = df_top_10.groupby('group')['y'].transform(lambda x: x.max() - x.min())


for g in df['group'].unique():
    g_value = df.loc[df['group'] == g, 'x']
    distance = g_value.max() - g_value.min()
    df.loc[df['group'] == g, 'distance'] = distance
'''

df_top_10 = df_top_10.iloc[:, [0, 1, 2, 3]]

#print(df[(df['y'] <= -0)])
#print(df_top_10[(df_top_10['y'] <= -2)])

print(df_top_10)
df_top_10.to_csv(r'..\trajectories\chosen_trajectories\test.csv', index=False)