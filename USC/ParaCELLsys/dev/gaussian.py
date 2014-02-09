import numpy as np
import Image
import math
from numbapro import cuda
from timeit import default_timer as timer

__author__ = 'mavinm'
__date__ = '2/5/14'


@cuda.jit('void(float32[:,:], float32[:,:], float32, float32, float32, float32, float32)', target='gpu')
def gaussian_blur(pts, pixels, sigma, dx, dy, axis_init_x, axis_init_y):
    gaussian_bottom = (2 * 3.14159265359 * sigma ** 2)
    m, n = pixels.shape
    num_points = pts.shape[0]

    for i in range(m):
        for j in range(n):
            for pt_num in range(num_points):
                val_x = j * dx + axis_init_x
                val_y = i * dy + axis_init_y
                gaussian_top = math.exp(
                    -((pts[pt_num, 0] - val_x) ** 2 + (pts[pt_num, 1] - val_y) ** 2) / (2 * sigma ** 2))
                pixels[i, j] += gaussian_top / gaussian_bottom


class GridGaussian():
    def __init__(self, pts, axis, split, sigma):
        if split[0] < 2 or split[1] < 2:
            raise ValueError("Split needs to be at least 2x2")

        dx = float((axis[1] - axis[0])) / float(split[0] - 1)
        dy = float((axis[3] - axis[2])) / float(split[1] - 1)

        self.pixels = np.zeros(split, dtype=np.float32)
        gpu_pts = cuda.to_device(pts)
        gaussian_blur(gpu_pts, self.pixels, float(sigma), dx, dy, float(axis[0]), float(axis[2]))

    def save_image(self):
        rescaled = (255.0 / self.pixels.max() * (self.pixels - self.pixels.min())).astype(np.uint8)
        im = Image.fromarray(rescaled)
        im.show()


a = np.array([[-3, 0], [2, 5], [0, 1]], dtype=np.float32)
start = timer()
g = GridGaussian(a, (-3, 4, -2, 5), (400, 400), 1)
dt = timer() - start
print "Gaussian Blur created on GPU in %f s" % dt
g.save_image()
