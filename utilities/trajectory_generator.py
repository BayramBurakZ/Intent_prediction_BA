import os
import pandas as pd
import numpy as np


def get_control_point(start, end, curvature):
    max_deviation = 0.5  # Maximum deviation in y-direction for maximum curvature
    deviation = curvature * max_deviation

    midpoint = (start + end) / 2
    direction_vector = end - start

    # direction of curvature depending on y-axis
    if end[1] > start[1]: # end point right side -> left curve
        orthogonal_vector = np.array([-direction_vector[1], direction_vector[0]])
    else: # end point left side -> right curve
        orthogonal_vector = np.array([direction_vector[1], -direction_vector[0]])

    # normalize
    orthogonal_vector = orthogonal_vector / np.linalg.norm(orthogonal_vector)

    control = midpoint + deviation * orthogonal_vector
    return control


# Function to calculate the quadratic Bézier curve
def calculate_quadratic_bezier_curve(start, end, curvature, num_points=1000):
    control = get_control_point(start, end, curvature)

    # Parameter variable t
    t = np.linspace(0, 1, num_points).reshape(-1, 1)

    # Calculate the quadratic Bézier curve
    curve = (1 - t) ** 2 * start + 2 * (1 - t) * t * control + t ** 2 * end

    return curve


def generate_trajectories_bezier(input_folder, output_folder, start_coords, curvature=0.5, steps=1000):
    assert os.path.exists(input_folder), 'input folder does not exist'
    assert os.path.exists(output_folder), 'output folder does not exist'

    match curvature:
        case 0.0:
            curve_type = 'linear'
        case 0.25:
            curve_type = 'gentle'
        case 0.5:
            curve_type = 'moderate'
        case 0.75:
            curve_type = 'sharp'
        case 1.0:
            curve_type = 'max'
        case _:
            curve_type = 'undefined'

    # Iterate through each file in the input folder
    for filename in os.listdir(input_folder):
        if filename.endswith('.csv'):
            # Read the CSV file
            file_path = os.path.join(input_folder, filename)
            df = pd.read_csv(file_path)

            for _, row in df.iterrows():
                # Get the ID and target coordinates
                target_id = int(row['ID'])
                target_coords = row[['x', 'y', 'z']].to_numpy()

                # Calculate quadratic Bezier curve in 2D
                start = start_coords[:2]
                end = target_coords[:2]
                curve_2d = calculate_quadratic_bezier_curve(start, end, curvature, steps)

                # Add z component with 1.0
                trajectory = np.hstack((curve_2d, np.ones((steps, 1))))

                # Save the trajectory to a new CSV file
                output_filename = f'traj_{curve_type}_{filename.split(".")[0]}_target_{target_id}.csv'
                output_path = os.path.join(output_folder, output_filename)
                trajectory_df = pd.DataFrame(trajectory, columns=['x', 'y', 'z'])
                trajectory_df.insert(0, 'time', pd.Series(range(1, steps + 1)))
                trajectory_df.to_csv(output_path, index=False)


# Usage
input_folder = r'../data/test_data/test_goal'  # Replace with your input folder path
output_folder = r'../data/test_data/test_trajectory/start_middle'  # Replace with your output folder path

start_coords = np.array([1.0, 0.0, 1.0])

print('generating test curves LINEAR')
generate_trajectories_bezier(input_folder, output_folder, start_coords, 0)
print('generating test curves GENTLE')
generate_trajectories_bezier(input_folder, output_folder, start_coords, 0.25)
print('generating test curves MODERATE')
generate_trajectories_bezier(input_folder, output_folder, start_coords, 0.5)
print('generating test curves SHARP')
generate_trajectories_bezier(input_folder, output_folder, start_coords, 0.75)
print('generating test curves MAX')
generate_trajectories_bezier(input_folder, output_folder, start_coords, 1)



