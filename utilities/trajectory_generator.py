import os

import numpy as np
import pandas as pd


def get_control_point(start, end, curvature):
    max_deviation = 0.7  # Maximum deviation in y-direction for maximum curvature
    deviation = curvature * max_deviation

    midpoint = (start + end) / 2  # control point is set at midpoint
    direction_vector = end - start

    # direction of curvature depending on y-axis
    if end[1] > start[1]:  # end point right side -> left curve
        orthogonal_vector = np.array([-direction_vector[1], direction_vector[0]])
    else:  # end point left side -> right curve
        orthogonal_vector = np.array([direction_vector[1], -direction_vector[0]])

    norm = np.linalg.norm(orthogonal_vector)  # normalize
    if norm < 1e-6:  # small threshold to check if the norm is effectively zero
        return None

    orthogonal_vector = orthogonal_vector / norm  # o.v. to deviate control point at middle
    return midpoint + deviation * orthogonal_vector


def calculate_quadratic_bezier_curve(start, end, curvature, num_points=1000):
    control = get_control_point(start, end, curvature)
    if control is None:
        return None

    t = np.linspace(0, 1, num_points).reshape(-1, 1)

    return (1 - t) ** 2 * start + 2 * (1 - t) * t * control + t ** 2 * end


def generate_trajectories_bezier(input_folder, output_folder, start_coords, hand, curvature=0.5, steps=1000):
    assert os.path.exists(input_folder), 'input folder does not exist'
    assert os.path.exists(output_folder), 'output folder does not exist'

    match curvature:
        case 0.0:
            curve_type = '0'
        case 0.5:
            curve_type = '1'
        case 1.0:
            curve_type = '2'
        case _:
            curve_type = 'undefined'

    # Iterate through each file in the input folder ( Test goals )
    for filename in os.listdir(input_folder):
        if filename.endswith('.csv'):

            goal_id = os.path.splitext(filename)[0]
            file_path = os.path.join(input_folder, filename)
            df = pd.read_csv(file_path)

            for _, row in df.iterrows():
                # Get the goal ID and coordinates
                target_id = int(row['ID'])
                target_coords = row[['x', 'y', 'z']].to_numpy()

                # Calculate quadratic Bezier curve without z component
                start = start_coords[:2]
                end = target_coords[:2]
                curve_2d = calculate_quadratic_bezier_curve(start, end, curvature, steps)
                if curve_2d is None:
                    break

                # Add z component with 1.0
                trajectory = np.hstack((curve_2d, np.ones((steps, 1))))
                trajectory_df = pd.DataFrame(trajectory, columns=['x', 'y', 'z'])
                trajectory_df.insert(0, 'time', pd.Series(range(1, steps + 1)))

                # Save the trajectory to a new CSV file
                output_filename = f'{goal_id}_{target_id}_{curve_type}{hand}.csv'
                output_path = os.path.join(output_folder, output_filename)
                trajectory_df.to_csv(output_path, index=False)


input_folder = r'../data/test_data_generated/test_goal'
output_folder = r'../data/test_data_generated/test_trajectory'

print('Middle:')
start_coords = np.array([1.0, 0.0, 1.0])
print('generating test curves LINEAR')
generate_trajectories_bezier(input_folder, output_folder, start_coords, '0', 0)
print('generating test curves MODERATE')
generate_trajectories_bezier(input_folder, output_folder, start_coords, '0', 0.5)
print('generating test curves MAX')
generate_trajectories_bezier(input_folder, output_folder, start_coords, '0', 1)

print('left:')
start_coords = np.array([1.0, -1.0, 1.0])
print('generating test curves LINEAR')
generate_trajectories_bezier(input_folder, output_folder, start_coords, '1', 0)
print('generating test curves MODERATE')
generate_trajectories_bezier(input_folder, output_folder, start_coords, '1', 0.5)
print('generating test curves MAX')
generate_trajectories_bezier(input_folder, output_folder, start_coords, '1', 1)

print('right:')
start_coords = np.array([1.0, 1.0, 1.0])
print('generating test curves LINEAR')
generate_trajectories_bezier(input_folder, output_folder, start_coords, '2', 0)
print('generating test curves MODERATE')
generate_trajectories_bezier(input_folder, output_folder, start_coords, '2', 0.5)
print('generating test curves MAX')
generate_trajectories_bezier(input_folder, output_folder, start_coords, '2', 1)
