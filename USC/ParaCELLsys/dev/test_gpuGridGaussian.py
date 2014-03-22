from unittest import TestCase
from dev.gaussian_gpu_grid import GpuGridGaussian
from gaussian_gpu import GpuGaussianOld
import numpy as np

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


class TestGpuGridGaussianCompute64x64(TestCase):
    def setUp(self):
        a = np.array([[0, 0], [1, 1], [0, 1], [1, 0], [.5, .5]]).astype(np.float32).reshape(5, 2)
        self.size = (64, 64)
        sigma = .1
        self.new = GpuGridGaussian(a, (0, 1, 0, 1), self.size, sigma)
        self.new.compute_grid()
        self.old = GpuGaussianOld(a, (0, 1, 0, 1), self.size, sigma)
        self.old.compute_grid()

    def doCleanups(self):
        self.new.clean_cuda()
        self.old.clean_cuda()

    def test_equal_arrays(self):
        new_data = self.new.get_grid_data()
        old_data = self.old.get_grid_data()
        self.new.show_image()
        self.old.show_image()
        assert np.array_equal(new_data, old_data)

    def test_size(self):
        new_data = self.new.get_grid_data()
        assert new_data.shape == self.size

