import numpy as np


class Goal:
    """ A class that represents a goal.

    Attributes:
        num: (int)                      id of goal
        pos: (NDArray[np.float64])      coordinates of goal

        active: (bool)                  status of goal
        dist: (float)                   distance to last measured hand wrist
        prev_dist: (float)              distance to previous measured hand wrist
        mat: (NDArray[np.float64])      trajectory to goal as matrix
        dmat: (NDArray[np.float64])     derivative of trajectory matrix
        ppt: (NDArray[np.float64])      predicted point on the trajectory
        dppt: (NDArray[np.float64])     derivative at predicted point

        angle: (float)                  angle between last measured and predicted direction
        prob: (float)                   accumulated probability of samples
        sq: (int)                       sample quantity
    """

    def __init__(self, number, position):
        self.num = number
        self.pos = position
        self.active = True

        # prediction model
        self.dist = 0.0
        self.prev_dist = 0.0
        self.mat = None
        self.dmat = None
        self.ppt = None
        self.dppt = None
        self.angle = np.pi

        # probability
        self.prob = 0.0
        self.sq = 0

    def set_distance(self, curr_p):
        self.prev_dist = self.dist
        self.dist = np.linalg.norm(curr_p - self.pos)

    def set_matrices(self, mat):
        self.mat = mat[0]
        self.dmat = mat[1]

    def set_progression(self, progression):
        """ :param progression: (float)     progression along the trajectory """

        self.ppt = calc_poly(self.mat, progression)
        self.dppt = calc_poly(self.dmat, progression)

    def update_probability(self, prob_last):
        """ :param prob_last: (float)   probability of last measured angle """

        # lower boundary for probability at 1%
        min_probability = 0.001

        if prob_last < min_probability or self.prev_dist < self.dist:  # reset
            self.prob = 0.0
            self.sq = 0

        elif self.prob < min_probability:  # begin
            self.prob = prob_last
            self.sq = 1

        else:  # update
            self.prob *= prob_last
            self.sq += 1

    def normalize_probability(self, divisor):
        self.prob /= divisor

    def get_stats(self):
        return f'num: {self.num}| prob: {self.prob}| sq: {self.sq}| angle: {self.angle}'


def calc_poly(matrix, s):
    """ Calculates the value of a polynomial at point s. """
    x = np.polyval(matrix[0], s)
    y = np.polyval(matrix[1], s)
    z = np.polyval(matrix[2], s)

    return np.array([x, y, z])
