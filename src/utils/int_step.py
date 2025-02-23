import numpy as np

class IntegerStep:
    def __init__(self, stepsize=1):
        self.stepsize = stepsize

    def __call__(self, x):
        """
        make sure every step is integer
        param x: numpy.ndarray
        return new point
        """
        step = np.random.randint(-self.stepsize, self.stepsize + 1, size=x.shape)
        new_x = x + step
        return new_x
