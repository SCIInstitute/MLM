import math
import os

# Make sure pycuda.autoinit is initiated
import pycuda.autoinit
from pycuda.compiler import SourceModule
import pycuda.driver as cuda
import time
from convertGaussian2Image import *
from models import getFilteredDataSet


__author__ = 'mavinm'
__date__ = '2/5/14'


class GpuGridGaussian():
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
    __global__ void gpu_gaussian(float *grid, float *pts, int blockIdx_x, int blockIdx_y, int gridDim_x, int gridDim_y, int pt_len, float dx, float dy, float sigma)
    {
        float gaussian_bottom = (2 * CUDART_PI_F * pow(sigma, 2));

        int idx = threadIdx.y * blockDim.x * gridDim_x + blockIdx_y * blockDim.y * blockDim.x * gridDim_x + (threadIdx.x + blockIdx_x * blockDim.x);

        for (int pt_num = 0; pt_num < pt_len; pt_num++){
            float pt_x = pts[pt_num * 2];
            float pt_y = pts[pt_num * 2 + 1];
            float val_x = map_index_x(blockIdx_x * blockDim.x + threadIdx.x, dx);
            float val_y = map_index_y(blockIdx_y * blockDim.y + threadIdx.y, dy);
            float gaussian_top = expf(-(dist_squared(pt_x, val_x) + dist_squared(pt_y, val_y)) / (2 * pow(sigma, 2)));
            grid[idx] += gaussian_top/gaussian_bottom;
        }
    }
    """

    def __init__(self, view_tile, size, sigma, debug=False):
        self.debug = debug
        if size[0] < 2 or size[1] < 2:
            raise ValueError("Split needs to be at least 2x2")

        self.data_sets = view_tile.get_Data()
        for dset in self.data_sets:
            data = dset.getDataSet()
            if not data.flags['C_CONTIGUOUS']:
                print "NOT CONTIGUOUS, trying to reformat the points"
                data = np.require(data, dtype=data.dtype, requirements=['C'])
                if not data.flags['C_CONTIGUOUS']:
                    raise Exception("Points are not contiguous")
                dset.setDataSet(data)

        self.view_tile = view_tile
        self.sigma = sigma
        self.pts_gpu = None

        # Initiates all of cuda stuff
        self.grid = np.zeros(size).astype(np.float32)
        self.grid_gpu = cuda.mem_alloc_like(self.grid)
        cuda.memcpy_htod(self.grid_gpu, self.grid)

        kernel = SourceModule(self.__cuda_code)
        self.gpu_gaussian = kernel.get_function("gpu_gaussian")

        self.view = self.view_tile.get_View()

        self.grid_size, self.block_size = self.__setup_cuda_sizes(size)

        self.dx = 1 / float(size[1] - 1)
        self.dy = 1 / float(size[0] - 1)

    def __compute_guassian_on_pts(self):
        view = self.view_tile.get_View()

        for dset in self.data_sets:
            _data = np.array(dset.getDataSet(), copy=True)
            _data[:, 0] = (_data[:, 0] - view.left)/view.width()
            _data[:, 1] = (_data[:, 1] - view.bottom)/view.height()

            for row in range(self.grid_size[0]):
                for col in range(self.grid_size[1]):
                    # 3 * SIGMA give the 95%
                    left = 1 / float(self.grid_size[1]) * col - (3 * self.sigma)
                    right = 1 / float(self.grid_size[1]) * (col + 1) + (3 * self.sigma)
                    bottom = 1 / float(self.grid_size[0]) * row - (3 * self.sigma)
                    top = 1 / float(self.grid_size[0]) * (row + 1) + (3 * self.sigma)
                    pts = getFilteredDataSet(_data, (left, right, bottom, top))

                    if len(pts) > 0:
                        self.pts_gpu = cuda.mem_alloc_like(pts)
                        cuda.memcpy_htod(self.pts_gpu, pts)

                        self.gpu_gaussian(self.grid_gpu,  # Grid
                                          self.pts_gpu,  # Points
                                          np.int32(col),  # Block Index x
                                          np.int32(row),  # Block Index y
                                          np.int32(self.grid_size[1]),  # Grid Dimensions x
                                          np.int32(self.grid_size[0]),  # Grid Dimensions y
                                          np.int32(pts.shape[0]),  # Point Length
                                          np.float32(self.dx),  # dx
                                          np.float32(self.dy),  # dy
                                          np.float32(self.sigma),  # Sigma
                                          block=self.block_size)

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

        if split[0] <= max_threads_sr and split[1] <= max_threads_sr:
            block_size = (split[0], split[1], 1)
            grid_size = (1, 1)
        else:
            if split[0] % max_threads_sr != 0 or split[1] % max_threads_sr != 0:
                raise ValueError("Only supports multiples of %i" % max_threads_sr)
            size_m = split[0] / max_threads_sr
            size_n = split[1] / max_threads_sr
            grid_size = (size_m, size_n)
            block_size = (max_threads_sr, max_threads_sr, 1)
        return grid_size, block_size

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
        self.__compute_guassian_on_pts()
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