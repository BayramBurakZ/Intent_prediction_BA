from collections import deque

import numpy as np

"""
This file contains the following three classes for reducing noise and stabilizing data:
In general, a larger window (alpha) results in smoother data but is less responsive to sudden changes.

1. Simple Moving Average (SMA):
    - Not ideal for sudden changes.
    - Parameter: window size (integer greater than 1).

2. Weighted Moving Average (WMA):
    - Better for handling sudden changes.
    - Parameter: window size (integer greater than 1).

3. Exponential Moving Average (EMA):
    - Best for handling sudden changes.
    - Parameter: alpha (float between 0 and 1).
"""


class SimpleMovingAverage:
    def __init__(self, window_size):
        if window_size < 1:
            raise ValueError("window_size must be greater than 1.")

        self.window_size = window_size
        self.x_points = deque(maxlen=window_size)
        self.y_points = deque(maxlen=window_size)
        self.z_points = deque(maxlen=window_size)
        self.sum_x = 0.0
        self.sum_y = 0.0
        self.sum_z = 0.0

    def add(self, coordinates):
        if len(self.x_points) == self.window_size:  # delete the oldest value from sum
            self.sum_x -= self.x_points[0]
            self.sum_y -= self.y_points[0]
            self.sum_z -= self.z_points[0]

        # update the queue by removing the oldest value
        self.x_points.append(coordinates[0])
        self.sum_x += coordinates[0]
        self.y_points.append(coordinates[1])
        self.sum_y += coordinates[1]
        self.z_points.append(coordinates[2])
        self.sum_z += coordinates[2]

    def get(self):
        count = len(self.x_points)
        return np.array([self.sum_x / count, self.sum_y / count, self.sum_z / count]) if count != 0 else None


class WeightedMovingAverage:
    def __init__(self, window_size):
        if window_size < 1:
            raise ValueError("window_size must be greater than 1.")

        self.window_size = window_size
        self.weights = [i + 1 for i in range(window_size)]  # Weights: 1, 2, ..., window_size
        self.weight_sum = sum(self.weights)
        self.x_points = deque(maxlen=window_size)
        self.y_points = deque(maxlen=window_size)
        self.z_points = deque(maxlen=window_size)

    def add(self, coordinates):
        self.x_points.append(coordinates[0])
        self.y_points.append(coordinates[1])
        self.z_points.append(coordinates[2])

    def get(self):
        if len(self.x_points) == 0:
            return None

        wma_x = sum(w * x for w, x in zip(self.weights[-len(self.x_points):], self.x_points)) / self.weight_sum
        wma_y = sum(w * y for w, y in zip(self.weights[-len(self.y_points):], self.y_points)) / self.weight_sum
        wma_z = sum(w * z for w, z in zip(self.weights[-len(self.z_points):], self.z_points)) / self.weight_sum

        return np.array([wma_x, wma_y, wma_z])


class ExponentialMovingAverage:
    def __init__(self, alpha):
        if alpha > 1 or alpha < 0:
            raise ValueError("alpha must be between 0 and 1.")

        self.alpha = alpha
        self.ema_x = None
        self.ema_y = None
        self.ema_z = None

    def add(self, coordinates):
        if self.ema_x is None:  # Initialize EMA with the first data point
            self.ema_x = coordinates[0]
            self.ema_y = coordinates[1]
            self.ema_z = coordinates[2]
        else:
            self.ema_x = self.alpha * coordinates[0] + (1 - self.alpha) * self.ema_x
            self.ema_y = self.alpha * coordinates[1] + (1 - self.alpha) * self.ema_y
            self.ema_z = self.alpha * coordinates[2] + (1 - self.alpha) * self.ema_z

    def get(self):
        return np.array([self.ema_x, self.ema_y, self.ema_z]) if self.ema_x is not None else None
