import Image
import numpy as np

# Make sure pycuda.autoinit is initiated
import pycuda.autoinit
from pycuda.compiler import SourceModule
import pycuda.driver as cuda
import time


__author__ = 'mavinm'
__date__ = '2/5/14'


class GpuGridGaussian():
    cuda_code = """
    #define CUDART_PI_F 3.141592654f

    /**
     * Computes the distance between values squared
     */
    __device__ float dist_squared(float val1, float val2)
    {
        return pow(val1 - val2, 2);
    }

    /**
     * Maps the index of the grid cell on the x
     */
    __device__ float map_index_x(int x, float dx, float start){
        return x * dx + start;
    }

    /**
     * Maps the index of the grid cell on the y
     */
    __device__ float map_index_y(int y, float dy, float start){
        return y * dy + start;
    }

    /**
     * Computes the grid values of the gaussian
     */
    __global__ void gpu_gaussian(float *grid, float *pts, int pt_len, float dx, float dy, float start_x, float start_y, float sigma)
    {
        float gaussian_bottom = (2 * CUDART_PI_F * pow(sigma, 2));

        int idx = threadIdx.x + threadIdx.y * blockDim.x;

        for (int pt_num = 0; pt_num < pt_len; pt_num++){
            float pt_x = pts[pt_num * 2];
            float pt_y = pts[pt_num * 2 + 1];
            float val_x = map_index_x(threadIdx.x, dx, start_x);
            float val_y = map_index_y(threadIdx.y, dy, start_y);
            float gaussian_top = expf(-(dist_squared(pt_x, val_x) + dist_squared(pt_y, val_y)) / (2 * pow(sigma, 2)));
            grid[idx] += gaussian_top/gaussian_bottom;
        }
    }
    """

    def __init__(self, pts, axis, split, sigma):
        if split[0] < 2 or split[1] < 2:
            raise ValueError("Split needs to be at least 2x2")

        # Initiates all of cuda stuff
        self.grid = np.zeros(split).astype(np.float32)
        self.grid_gpu = cuda.mem_alloc_like(self.grid)
        cuda.memcpy_htod(self.grid_gpu, self.grid)

        self.pts_gpu = cuda.mem_alloc_like(pts)
        cuda.memcpy_htod(self.pts_gpu, pts)

        kernel = SourceModule(self.cuda_code)
        gpu_gaussian = kernel.get_function("gpu_gaussian")

        dx = float((axis[1] - axis[0])) / float(split[0] - 1)
        dy = float((axis[3] - axis[2])) / float(split[1] - 1)

        gpu_gaussian(self.grid_gpu,  # Grid
                     self.pts_gpu,  # Points
                     np.int32(pts.shape[0]),  # Point Length
                     np.float32(dx),  # dx
                     np.float32(dy),  # dy
                     np.float32(axis[0]),  # X Starting Point
                     np.float32(axis[2]),  # Y Starting Point
                     np.float32(sigma),  # Sigma
                     block=(split[0], split[1], 1))

        cuda.memcpy_dtoh(self.grid, self.grid_gpu)

        self.clean_cuda()

    def save_image(self):
        """
        Saves image to texture
        """
        rescaled = (255.0 / self.grid.max() * (self.grid - self.grid.min())).astype(np.uint8)
        im = Image.fromarray(rescaled)
        im.show()

    def clean_cuda(self):
        """
        Cleans up cuda code
        """
        self.grid_gpu.free()
        self.pts_gpu.free()


start = time.time()
a = np.array([[-3, 0], [2, 5], [2, 2]]).astype(np.float32)
g = GpuGridGaussian(a, (-3, 4, -2, 5), (32, 32), 1)
dt = time.time() - start
print "Gaussian Blur created on GPU in %f s" % dt
g.save_image()