import pandas as pd
import numpy as np
import csv

#select trajectory number
number = 16
path = r'trajectories\raw_trajectories\hand_tracking'
path += str(number) + '.csv'


# correcting parse error (more data than columns)
# function to get max field number
def max_fields(path):
    max_fields = 0
    with open(path, 'r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        for row in reader:
            # save max field
            if len(row) > max_fields:
                max_fields = len(row)
    return max_fields


#new column names to
columns = ['time', 'hand', 'x', 'y', 'z']
for x in range(max_fields(path) - 4):
    columns.append(str(x))

df = pd.read_csv(path, header=None, names=columns)

# Keep only the first five columns
df = df.iloc[:, [0, 1, 2, 3, 4]]


### remove possible mistakes
def is_convertible_to_uint(value):
    try:
        np.uint(value)
        return True
    except (ValueError, OverflowError):
        return False


def is_convertible_to_float32(value):
    try:
        np.float32(value)
        return True
    except (ValueError, OverflowError):
        return False

df_length=len(df.index)

df = df[df['time'].apply(is_convertible_to_uint)]
df = df[df['x'].apply(is_convertible_to_float32)]
df = df[df['y'].apply(is_convertible_to_float32)]
df = df[df['z'].apply(is_convertible_to_float32)]
df = df[df['hand'].isin(['right', 'left'])]
###

df['time'] = df['time'].astype(np.uint)
df['hand'] = df['hand'].astype(str)
df['x'] = df['x'].astype(np.float32)
df['y'] = df['y'].astype(np.float32)
df['z'] = df['z'].astype(np.float32)

df_right = df[df['hand'] == 'right']
df_left = df[df['hand'] == 'left']

df_right = df_right.drop('hand', axis=1)
df_left = df_left.drop('hand', axis=1)

# Sort DataFrame by 'time' in ascending order
df_right = df_right.sort_values(by='time', ascending=True)
df_left = df_left.sort_values(by='time', ascending=True)

print('-----> '+ str(df_length - (len(df_right.index) + len(df_left.index) )) + ' bad lines have been deleted' )
#print(df_right)
#print(df_left)

# Save the filtered DataFrames to new CSV files
df_right.to_csv(r'trajectories\right_hand\right_' + str(number) + '.csv', index=False)
df_left.to_csv(r'trajectories\left_hand\left_' + str(number) + '.csv', index=False)
