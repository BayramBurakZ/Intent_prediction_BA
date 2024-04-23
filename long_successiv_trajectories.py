import pandas as pd

path = r'trajectories\right_hand\right_2.csv'
df = pd.read_csv(path)
# new column 'increasing', True if the following line is greater
df['increasing'] = (df['time'].diff() > 0) & (df['x'].diff() > 0) & (df['y'].diff() > 0) & (df['z'].diff() > 0)

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

print(df_top_10)
