import pandas as pd
import matplotlib.pyplot as plt
import os


def plot_trajectory_from_csv(csv_file):
    data = pd.read_csv(csv_file)

    # Check if the necessary columns are present
    required_columns = ['time', 'x', 'y']
    if not all(column in data.columns for column in required_columns):
        raise ValueError(f'The CSV file must contain the following columns: {", ".join(required_columns)}')

    x = data['x']
    y = data['y']

    # Create a 2D plot
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111)
    ax.plot(x, y, label='Trajectory')
    ax.scatter(x, y, c='r')  # Optional: in case of reducing the number size

    # Label the axes
    ax.set_xlim(-1.1,1.1)
    ax.set_ylim(-1.1, 1.1)
    ax.set_xlabel('X')
    ax.set_ylabel('Y')
    ax.set_title('2D Trajectory Plot')
    ax.legend()

    plt.show()


path1 = r'../data/test_data_set1/test_trajectory/1_3_1_20.csv'
path2 = r'../data/test_data_set1/test_trajectory/2_5_1_20.csv'
path3 = r'../data/test_data_set1/test_trajectory/3_7_1_20.csv'
path4 = r'../data/test_data_set1/test_trajectory/4_3_1_11.csv'
path5 = r'../data/test_data_set1/test_trajectory/4_3_1_02.csv'

plot_trajectory_from_csv(path1)
plot_trajectory_from_csv(path2)
plot_trajectory_from_csv(path3)
plot_trajectory_from_csv(path4)
plot_trajectory_from_csv(path5)

os._exit(0)
