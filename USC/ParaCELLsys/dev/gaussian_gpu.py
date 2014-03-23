import math
import os

# Make sure pycuda.autoinit is initiated
import pycuda.autoinit
from pycuda.compiler import SourceModule
import pycuda.driver as cuda
import time
from convertGaussian2Image import *


__author__ = 'mavinm'
__date__ = '2/5/14'


class GpuGaussianOld():
    """
    @deprecated
    """
    __cuda_code = """
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
    __device__ float map_index_x(int x, float dx){
        return x * dx;
    }

    /**
     * Maps the index of the grid cell on the y
     */
    __device__ float map_index_y(int y, float dy){
        return y * dy;
    }

    /**
     * Computes the grid values of the gaussian
     */
    __global__ void gpu_gaussian(float *grid, float *pts, int pt_len, float dx, float dy, float sigma)
    {
        float gaussian_bottom = (2 * CUDART_PI_F * pow(sigma, 2));

        int idx = threadIdx.y * blockDim.x * gridDim.x + blockIdx.y * blockDim.y * blockDim.x * gridDim.y + (threadIdx.x + blockIdx.x * blockDim.x);

        for (int pt_num = 0; pt_num < pt_len; pt_num++){
            float pt_x = pts[pt_num * 2];
            float pt_y = pts[pt_num * 2 + 1];
            float val_x = map_index_x(blockIdx.x * blockDim.x + threadIdx.x, dx);
            float val_y = map_index_y(blockIdx.y * blockDim.y + threadIdx.y, dy);
            float gaussian_top = expf(-(dist_squared(pt_x, val_x) + dist_squared(pt_y, val_y)) / (2 * pow(sigma, 2)));
            grid[idx] += gaussian_top/gaussian_bottom;
        }
    }
    """

    def __init__(self, pts, axis, split, sigma):
        if split[0] < 2 or split[1] < 2:
            raise ValueError("Split needs to be at least 2x2")

        if not pts.flags['C_CONTIGUOUS']:
            pts = np.require(pts, dtype=pts.dtype, requirements=['C'])
            if not pts.flags['C_CONTIGUOUS']:
                raise Exception("Points are not contiguous")

        self.axis = axis
        self.sigma = sigma
        self.pts = pts
        self.pts_gpu = None

        # Initiates all of cuda stuff
        self.grid = np.zeros(split).astype(pts.dtype)
        self.grid_gpu = cuda.mem_alloc_like(self.grid)
        cuda.memcpy_htod(self.grid_gpu, self.grid)

        kernel = SourceModule(self.__cuda_code)
        self.gpu_gaussian = kernel.get_function("gpu_gaussian")

        self.dx = 1 / float(split[0] - 1)
        self.dy = 1 / float(split[1] - 1)

        self.grid_size, self.block_size = self.__setup_cuda_sizes(split)

    def __compute_guassian_on_pts(self, pts):
        cuda.memcpy_htod(self.pts_gpu, pts)

        self.gpu_gaussian(self.grid_gpu,  # Grid
                          self.pts_gpu,  # Points
                          np.int32(pts.shape[0]),  # Point Length
                          np.float32(self.dx),  # dx
                          np.float32(self.dy),  # dy
                          np.float32(self.sigma),  # Sigma
                          block=self.block_size,
                          grid=self.grid_size)

    def __compute_sub_gaussian_gpu(self, sub_partitions):
        if sub_partitions < 1:
            raise Exception("You can't have less than 1 partition")
        elif sub_partitions > self.pts.shape[0]:
            raise Exception("sub partitions need to be smaller than pts size")
        # Delta Partitions
        d_part = self.pts.shape[0]/sub_partitions

        # Does the correct partitioning
        alloc_size = self.pts.shape[0]/sub_partitions * 2 * self.pts.itemsize
        self.pts_gpu = cuda.mem_alloc(alloc_size)
        self.pts[:, 0] = (self.pts[:, 0] - self.axis[0])/(self.axis[1] - self.axis[0])
        self.pts[:, 1] = (self.pts[:, 1] - self.axis[2])/(self.axis[3] - self.axis[2])

        for partition in range(sub_partitions):
            sub_pts = self.pts[partition*d_part:(partition+1)*d_part, :]
            self.__compute_guassian_on_pts(sub_pts)
        self.pts_gpu.free()

        # See's if there is a remainder of points to work with
        if self.pts.shape[0] % sub_partitions:
            alloc_size = (self.pts.shape[0] % sub_partitions) * (2 * self.pts.itemsize)
            self.pts_gpu = cuda.mem_alloc(alloc_size)
            self.__compute_guassian_on_pts(self.pts[sub_partitions*d_part:, :])
            self.pts_gpu.free()

    def __setup_cuda_sizes(self, split):
        """
        Sets up the size of the cuda dimensional array

        Looks for an even square from cuda cores available
        @param split:
        @return:
        """
        max_threads = cuda.Device(0).get_attribute(cuda.device_attribute.MAX_THREADS_PER_BLOCK)

        # Square Root
        max_threads_sr = int(math.sqrt(max_threads))

        if split[0] <= max_threads_sr:
            block_size = (split[0], split[1], 1)
            grid_size = (1, 1, 1)
        else:
            if split[0] % max_threads_sr != 0 or split[1] % max_threads_sr != 0:
                raise ValueError("Only supports multiples of %i" % max_threads_sr)
            size_ = split[0] / max_threads_sr
            block_size = (max_threads_sr, max_threads_sr, 1)
            grid_size = (size_, size_, 1)
        return grid_size, block_size

    def __cuda_logic_partitions(self):
        # TODO - 1e4 is not a good number to use.  We should check the CUDA device properties to find a good value dependent on computer
        return int(math.ceil(self.pts.nbytes/1e4))

    def save_image(self, filename):
        """
        Saves image to texture
        """

        # Create directory 'tmp' if it does not exist
        dir = filename.split('/')
        if not os.path.exists(dir[-2]):
            os.mkdir(dir[-2])

        f = file(filename, "wb")
        np.save(f, self.grid)
        f.close()

    def show_image(self):
        rescaled = rescale_data_to_image(self.grid)
        im = Image.fromarray(rescaled)
        im.show()

    def compute_grid(self):
        self.__compute_sub_gaussian_gpu(self.__cuda_logic_partitions())
        cuda.memcpy_dtoh(self.grid, self.grid_gpu)

    def get_grid_data(self):
        """
        Returns the grid, make sure to call compute_grid first
        """
        return self.grid

    def clean_cuda(self):
        """
        Cleans up cuda code
        """
        self.grid_gpu.free()