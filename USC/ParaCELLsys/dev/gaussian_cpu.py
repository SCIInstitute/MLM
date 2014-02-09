import matplotlib.pyplot as plt
import numpy as np
import Image
import math
from timeit import default_timer as timer

__author__ = 'mavinm'
__date__ = '2/5/14'


def dist_squared(val1, val2):
    return (val1 - val2) ** 2


class GridGaussian():

    def __init__(self, array, axis, split, sigma):
        if split[0] < 2 or split[1] < 2:
            raise ValueError("Split needs to be at least 2x2")

        self.axis = axis
        self.split = split
        self.dx = float((axis[1] - axis[0])) / float(split[0] - 1)
        self.dy = float((axis[3] - axis[2])) / float(split[1] - 1)

        self.pixels = np.zeros(split)

        self.gaussian_evaluate_pixels(array, sigma)

    def save_image(self):
        rescaled = (255.0 / self.pixels.max() * (self.pixels - self.pixels.min())).astype(np.uint8)
        im = Image.fromarray(rescaled)
        im.show()

    def gaussian_evaluate_pixels(self, array, sigma):
        gaussian_bottom = (2 * math.pi * sigma ** 2)
        for pt in array:
            for i in range(0, self.split[0]):
                for j in range(0, self.split[1]):
                    val_x, val_y = self.map_index(j, i)
                    gaussian_top = math.exp(
                        -(dist_squared(pt[0], val_x) + dist_squared(pt[1], val_y)) / (2 * sigma ** 2))
                    self.pixels[i][j] += gaussian_top / gaussian_bottom

    def map_index(self, x, y):
        val_x = x * self.dx + self.axis[0]
        val_y = y * self.dy + self.axis[2]
        return val_x, val_y

start = timer()
a = np.array([[-3, 0], [2, 5]])
g = GridGaussian(a, (-3, 4, -2, 5), (500, 500), 1)
dt = timer() - start
print "Gaussian Blur created on CPU in %f s" % dt
g.save_image()