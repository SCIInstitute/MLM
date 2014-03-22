from unittest import TestCase
from dev.gaussian_cpu import CpuGridGaussian
from dev.gaussian_gpu_grid import GpuGridGaussian
from gaussian_gpu import GpuGaussianOld
import numpy as np
from models import CellTypeDataSet
from view import ViewTile

__author__ = 'mavinm'
__date__ = '3/22/14'


class TestGpuGridGaussianNoCompute(TestCase):
    def setUp(self):
        a = np.array([[0, 0], [1, 1], [0, 1], [1, 0], [.5, .5]]).astype(np.float32).reshape(5, 2)
        self.g = GpuGridGaussian(a, (0, 1, 0, 1), (32, 32), .1)

    def doCleanups(self):
        self.g.clean_cuda()

    def test_array_equiv(self):
        image = self.g.get_grid_data()
        compare = np.zeros_like(image)
        assert np.array_equiv(image, compare)

    def test_array_equal(self):
        image = self.g.get_grid_data()
        compare = np.zeros_like(image)
        assert np.array_equal(image, compare)


class TestGpuGridGaussianCompute32x32(TestCase):
    def setUp(self):
        a = np.array([[0, 0], [1, 1], [0, 1], [1, 0], [.5, .5]]).astype(np.float32).reshape(5, 2)
        size = (32, 32)
        sigma = .1
        self.new = GpuGridGaussian(a, (0, 1, 0, 1), size, sigma)
        self.new.compute_grid()
        self.old = GpuGaussianOld(a, (0, 1, 0, 1), size, sigma)
        self.old.compute_grid()

    def doCleanups(self):
        self.new.clean_cuda()
        self.old.clean_cuda()

    def test_equiv_arrays(self):
        new_data = self.new.get_grid_data()
        old_data = self.old.get_grid_data()
        assert np.array_equiv(new_data, old_data)

    def test_equal_arrays(self):
        new_data = self.new.get_grid_data()
        old_data = self.old.get_grid_data()
        assert np.array_equal(new_data, old_data)

    def test_size(self):
        new_data = self.new.get_grid_data()
        assert new_data.shape == (32, 32)


class TestGpuGridGaussianCompute2x2(TestCase):
    def setUp(self):
        a = np.array([[0, 0], [1, 1], [0, 1], [1, 0], [.5, .5]]).astype(np.float32).reshape(5, 2)
        self.size = (2, 2)
        sigma = .1
        self.new = GpuGridGaussian(a, (0, 1, 0, 1), self.size, sigma)
        self.new.compute_grid()
        self.old = GpuGaussianOld(a, (0, 1, 0, 1), self.size, sigma)
        self.old.compute_grid()

    def doCleanups(self):
        self.new.clean_cuda()
        self.old.clean_cuda()

    def test_equiv_arrays(self):
        new_data = self.new.get_grid_data()
        old_data = self.old.get_grid_data()
        assert np.array_equiv(new_data, old_data)

    def test_equal_arrays(self):
        new_data = self.new.get_grid_data()
        old_data = self.old.get_grid_data()
        assert np.array_equal(new_data, old_data)

    def test_size(self):
        new_data = self.new.get_grid_data()
        assert new_data.shape == self.size
        old_data = self.old.get_grid_data()
        assert old_data.shape == self.size


class TestGpuGridGaussianCompute32x32(TestCase):
    def setUp(self):
        a = np.array([[3, 3], [5, 5], [3, 3], [5, 5], [4, 4]]).astype(np.float32).reshape(5, 2)
        self.grid_size = (32, 32)
        sigma = .07

        test_set = CellTypeDataSet("GC Cell Septotemporal Position (mm)", a, rgb=(0, .5, .5))

        # These are the individual tiles that will have information about the dataset
        test_tile = ViewTile((test_set,), (3, 5, 3, 5))

        self.new = GpuGridGaussian(test_tile, self.grid_size, sigma)
        self.new.compute_grid()
        self.old = GpuGaussianOld(test_tile.get_Data()[0].getDataSet(), test_tile.get_View().view(), self.grid_size, sigma)
        self.old.compute_grid()

    def doCleanups(self):
        self.new.clean_cuda()
        self.old.clean_cuda()

    def test_shape(self):
        new_data = self.new.get_grid_data()
        old_data = self.old.get_grid_data()
        assert new_data.shape == old_data.shape

    def test_equiv_arrays(self):
        new_data = self.new.get_grid_data()
        old_data = self.old.get_grid_data()
        assert np.allclose(new_data, old_data)

    def test_equal_arrays(self):
        new_data = self.new.get_grid_data()
        old_data = self.old.get_grid_data()
        assert np.allclose(new_data, old_data)

    def test_size(self):
        new_data = self.new.get_grid_data()
        assert new_data.shape == self.grid_size


class TestGpuGridGaussianCompute64x64(TestCase):
    def setUp(self):
        a = np.array([[3, 3], [5, 5], [3, 5], [5, 3], [4, 4]]).astype(np.float32).reshape(5, 2)
        self.grid_size = (64, 64)
        sigma = .15

        test_set = CellTypeDataSet("GC Cell Septotemporal Position (mm)", a, rgb=(0, .5, .5))

        # These are the individual tiles that will have information about the dataset
        test_tile = ViewTile((test_set,), (3, 5, 3, 5))

        self.new = GpuGridGaussian(test_tile, self.grid_size, sigma)
        self.new.compute_grid()
        self.old = GpuGaussianOld(test_tile.get_Data()[0].getDataSet(), test_tile.get_View().view(), self.grid_size, sigma)
        self.old.compute_grid()

    def doCleanups(self):
        self.new.clean_cuda()
        self.old.clean_cuda()

    def test_shape(self):
        new_data = self.new.get_grid_data()
        old_data = self.old.get_grid_data()
        assert new_data.shape == old_data.shape

    def test_equiv_arrays(self):
        new_data = self.new.get_grid_data()
        old_data = self.old.get_grid_data()
        assert np.allclose(new_data, old_data)

    def test_equal_arrays(self):
        new_data = self.new.get_grid_data()
        old_data = self.old.get_grid_data()
        assert np.allclose(new_data, old_data)

    def test_size(self):
        new_data = self.new.get_grid_data()
        assert new_data.shape == self.grid_size


class TestGpuGridGaussianComputeComplex64x64(TestCase):
    def setUp(self):
        a = np.array([[3, 3], [5, 5], [3, 5], [5, 3], [4.1, 4.1]]).astype(np.float32).reshape(5, 2)
        self.grid_size = (64, 64)
        sigma = .15

        test_set = CellTypeDataSet("GC Cell Septotemporal Position (mm)", a, rgb=(0, .5, .5))

        # These are the individual tiles that will have information about the dataset
        test_tile = ViewTile((test_set,), (3, 5, 3, 5))

        self.new = GpuGridGaussian(test_tile, self.grid_size, sigma)
        self.new.compute_grid()
        self.old = GpuGaussianOld(test_tile.get_Data()[0].getDataSet(), test_tile.get_View().view(), self.grid_size, sigma)
        self.old.compute_grid()

    def doCleanups(self):
        self.new.clean_cuda()
        self.old.clean_cuda()

    def test_shape(self):
        self.new.show_image()
        new_data = self.new.get_grid_data()
        old_data = self.old.get_grid_data()
        assert new_data.shape == old_data.shape

    def test_equiv_arrays(self):
        new_data = self.new.get_grid_data()
        old_data = self.old.get_grid_data()
        assert np.allclose(new_data, old_data)

    def test_equal_arrays(self):
        new_data = self.new.get_grid_data()
        old_data = self.old.get_grid_data()
        assert np.allclose(new_data, old_data)

    def test_size(self):
        new_data = self.new.get_grid_data()
        assert new_data.shape == self.grid_size


class TestGpuGridGaussianCompute128x128(TestCase):
    def setUp(self):
        a = np.array([[0, 0], [1, 1], [0, 1], [1, 0], [.5, .5]]).astype(np.float32).reshape(5, 2)
        self.size = (128, 128)
        sigma = .1
        self.new = GpuGridGaussian(a, (0, 1, 0, 1), self.size, sigma)
        self.new.compute_grid()
        self.old = GpuGaussianOld(a, (0, 1, 0, 1), self.size, sigma)
        self.old.compute_grid()

    def doCleanups(self):
        self.new.clean_cuda()
        self.old.clean_cuda()

    def test_shape(self):
        new_data = self.new.get_grid_data()
        old_data = self.old.get_grid_data()
        assert new_data.shape == old_data.shape

    def test_equal_arrays(self):
        new_data = self.new.get_grid_data()
        old_data = self.old.get_grid_data()
        assert np.array_equiv(new_data, old_data)

    def test_equal_arrays(self):
        new_data = self.new.get_grid_data()
        old_data = self.old.get_grid_data()
        assert np.array_equal(new_data, old_data)

    def test_size(self):
        new_data = self.new.get_grid_data()
        assert new_data.shape == self.size


class TestGpu2Cpu(TestCase):
    def setUp(self):
        a = np.array([[0, 0], [1, 1], [0, 1], [1, 0], [.5, .5]]).astype(np.float32).reshape(5, 2)
        self.size = (64, 64)
        sigma = .1
        self.gpu = GpuGridGaussian(a, (0, 1, 0, 1), self.size, sigma)
        self.gpu.compute_grid()
        self.cpu = CpuGridGaussian(a, (0, 1, 0, 1), self.size, sigma)

    def doCleanups(self):
        self.gpu.clean_cuda()

    def test_size(self):
        assert self.cpu.pixels.shape == self.gpu.get_grid_data().shape

    def test_equal_arrays(self):
        assert np.allclose(self.cpu.pixels, self.gpu.get_grid_data())

    def test_equiv_arrays(self):
        assert np.allclose(self.cpu.pixels, self.gpu.get_grid_data())