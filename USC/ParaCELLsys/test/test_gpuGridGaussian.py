from unittest import TestCase

import numpy as np
import math

from gaussian_gpu_grid import GpuGridGaussian
from dev.gaussian_gpu import GpuGaussianOld
from models import CellTypeDataSet, ParseParallelCellData
from view import ViewTile


__author__ = 'mavinm'
__date__ = '3/22/14'


def getDimensions(object):
    return tuple(map(int, object.__class__.__name__.split("_")[-1].split("x")))


def gaussian_normal_sigma(sigma):
    return 1/(2 * math.pi * sigma ** 2)


class TestGpuGridGaussianNoCompute(TestCase):
    def setUp(self):
        a = np.array([[0, 0], [1, 1], [0, 1], [1, 0], [.5, .5]]).astype(np.float32).reshape(5, 2)

        test_set = CellTypeDataSet("", a, rgb=(0, .5, .5))

        # These are the individual tiles that will have information about the dataset
        test_tile = ViewTile((test_set,), (0, 1, 0, 1))

        self.g = GpuGridGaussian(test_tile, (32, 32), .1)

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


class TestGpuGridGaussianCompute_32x32(TestCase):
    def setUp(self):
        self.size = getDimensions(self)
        a = np.array([[0, 0], [1, 1], [0, 1], [1, 0], [.5, .5]]).astype(np.float32).reshape(5, 2)
        sigma = .1
        test_set = CellTypeDataSet("", a, rgb=(0, .5, .5))
        test_tile = ViewTile((test_set,), (0, 1, 0, 1))
        self.new = GpuGridGaussian(test_tile, self.size, sigma)
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


class TestGpuGridGaussianCompute_64x32(TestCase):
    def setUp(self):
        self.size = getDimensions(self)
        a = np.array([[0, 0], [1, 1], [0, 1], [1, 0], [.5, .5]]).astype(np.float32).reshape(5, 2)
        self.sigma = .1

        test_set = CellTypeDataSet("", a, rgb=(0, .5, .5))

        # These are the individual tiles that will have information about the dataset
        test_tile = ViewTile((test_set,), (0, 1, 0, 1))

        self.new = GpuGridGaussian(test_tile, self.size, self.sigma)
        self.new.compute_grid()

    def doCleanups(self):
        self.new.clean_cuda()

    def test_shape(self):
        new_data = self.new.get_grid_data()
        assert new_data.shape == self.size

    def test_max_point_value(self):
        g = gaussian_normal_sigma(self.sigma)
        new_data = self.new.get_grid_data()
        diff = math.fabs(new_data.max() - g)
        assert diff < .00001

    def test_min_point_value(self):
        new_data = self.new.get_grid_data()
        assert new_data.min() < .001


class TestGpuGridGaussianComputeLargeGrid_128x64(TestCase):
    def setUp(self):
        self.size = getDimensions(self)
        a = np.array([[3, 10], [10, 100], [10, 10], [3, 100], [6.5, 55]]).astype(np.float32).reshape(5, 2)
        self.sigma = .1

        test_set = CellTypeDataSet("", a, rgb=(0, .5, .5))

        # These are the individual tiles that will have information about the dataset
        test_tile = ViewTile((test_set,), (3, 10, 10, 100))

        self.new = GpuGridGaussian(test_tile, self.size, self.sigma)
        self.new.compute_grid()

    def doCleanups(self):
        self.new.clean_cuda()

    def test_shape(self):
        new_data = self.new.get_grid_data()
        assert new_data.shape == self.size

    def test_max_point_value(self):
        g = gaussian_normal_sigma(self.sigma)
        new_data = self.new.get_grid_data()
        diff = math.fabs(new_data.max() - g)
        assert diff < .00001

    def test_min_point_value(self):
        new_data = self.new.get_grid_data()
        assert new_data.min() < .001


class TestGpuGridGaussianCompute_192x128(TestCase):
    def setUp(self):
        self.size = getDimensions(self)
        a = np.array([[0, 0], [1, 1], [0, 1], [1, 0], [.5, .5]]).astype(np.float32).reshape(5, 2)
        self.sigma = .1

        test_set = CellTypeDataSet("", a, rgb=(0, .5, .5))

        # These are the individual tiles that will have information about the dataset
        test_tile = ViewTile((test_set,), (0, 1, 0, 1))

        self.new = GpuGridGaussian(test_tile, self.size, self.sigma, debug=True)
        self.new.compute_grid()

    def doCleanups(self):
        self.new.clean_cuda()

    def test_shape(self):
        new_data = self.new.get_grid_data()
        assert new_data.shape == self.size

    def test_max_point_value(self):
        g = gaussian_normal_sigma(self.sigma)
        new_data = self.new.get_grid_data()
        diff = math.fabs(new_data.max() - g)
        assert diff < .00001

    def test_min_point_value(self):
        new_data = self.new.get_grid_data()
        assert new_data.min() < .001


class TestGpuGridGaussianCompute_512x256(TestCase):
    def setUp(self):
        self.size = getDimensions(self)
        a = np.array([[0, 0], [1, 1], [0, 1], [1, 0], [.5, .5]]).astype(np.float32).reshape(5, 2)
        self.sigma = .1

        test_set = CellTypeDataSet("", a, rgb=(0, .5, .5))

        # These are the individual tiles that will have information about the dataset
        test_tile = ViewTile((test_set,), (0, 1, 0, 1))

        self.new = GpuGridGaussian(test_tile, self.size, self.sigma)
        self.new.compute_grid()

    def doCleanups(self):
        self.new.clean_cuda()

    def test_shape(self):
        new_data = self.new.get_grid_data()
        assert new_data.shape == self.size

    def test_max_point_value(self):
        g = gaussian_normal_sigma(self.sigma)
        new_data = self.new.get_grid_data()
        diff = math.fabs(new_data.max() - g)
        assert diff < .00001

    def test_min_point_value(self):
        new_data = self.new.get_grid_data()
        assert new_data.min() < .001


class TestGpuGridGaussianCompute_96x96(TestCase):
    def setUp(self):
        self.size = getDimensions(self)
        a = np.array([[0, 0], [1, 1], [0, 1], [1, 0], [.5, .5]]).astype(np.float32).reshape(5, 2)
        self.sigma = .1

        test_set = CellTypeDataSet("", a, rgb=(0, .5, .5))

        # These are the individual tiles that will have information about the dataset
        test_tile = ViewTile((test_set,), (0, 1, 0, 1))

        self.new = GpuGridGaussian(test_tile, self.size, self.sigma)
        self.new.compute_grid()

    def doCleanups(self):
        self.new.clean_cuda()

    def test_shape(self):
        new_data = self.new.get_grid_data()
        assert new_data.shape == self.size

    def test_max_point_value(self):
        g = gaussian_normal_sigma(self.sigma)
        new_data = self.new.get_grid_data()
        diff = math.fabs(new_data.max() - g)
        assert diff < .00001

    def test_min_point_value(self):
        new_data = self.new.get_grid_data()
        assert new_data.min() < .001


class TestGpuGridGaussianCompute_64x128(TestCase):
    def setUp(self):
        self.size = getDimensions(self)
        a = np.array([[0, 0], [1, 1], [0, 1], [1, 0], [.5, .5]]).astype(np.float32).reshape(5, 2)
        self.sigma = .1

        test_set = CellTypeDataSet("", a, rgb=(0, .5, .5))

        # These are the individual tiles that will have information about the dataset
        test_tile = ViewTile((test_set,), (0, 1, 0, 1))

        self.new = GpuGridGaussian(test_tile, self.size, self.sigma)
        self.new.compute_grid()

    def doCleanups(self):
        self.new.clean_cuda()

    def test_shape(self):
        new_data = self.new.get_grid_data()
        assert new_data.shape == self.size

    def test_max_point_value(self):
        g = gaussian_normal_sigma(self.sigma)
        new_data = self.new.get_grid_data()
        diff = math.fabs(new_data.max() - g)
        assert diff < .00001

    def test_min_point_value(self):
        new_data = self.new.get_grid_data()
        assert new_data.min() < .001


class TestGpuGridGaussianCompute_32x64(TestCase):
    def setUp(self):
        self.size = getDimensions(self)
        a = np.array([[0, 0], [1, 1], [0, 1], [1, 0], [.5, .5]]).astype(np.float32).reshape(5, 2)
        self.sigma = .1

        test_set = CellTypeDataSet("", a, rgb=(0, .5, .5))

        # These are the individual tiles that will have information about the dataset
        test_tile = ViewTile((test_set,), (0, 1, 0, 1))

        self.new = GpuGridGaussian(test_tile, self.size, self.sigma)
        self.new.compute_grid()

    def doCleanups(self):
        self.new.clean_cuda()

    def test_shape(self):
        new_data = self.new.get_grid_data()
        assert new_data.shape == self.size

    def test_max_point_value(self):
        g = gaussian_normal_sigma(self.sigma)
        new_data = self.new.get_grid_data()
        diff = math.fabs(new_data.max() - g)
        assert diff < .00001

    def test_min_point_value(self):
        new_data = self.new.get_grid_data()
        assert new_data.min() < .001


class TestGpuGridGaussianCompute_1x1(TestCase):
    def test_failure(self):
        size = getDimensions(self)
        self.assertRaises(ValueError, GpuGridGaussian, None, size, .1)


class TestGpuGridGaussianCompute_2x2(TestCase):
    def setUp(self):
        self.size = getDimensions(self)
        a = np.array([[0, 0], [1, 1], [0, 1], [1, 0], [.5, .5]]).astype(np.float32).reshape(5, 2)
        sigma = .1

        test_set = CellTypeDataSet("", a, rgb=(0, .5, .5))

        # These are the individual tiles that will have information about the dataset
        test_tile = ViewTile((test_set,), (0, 1, 0, 1))

        self.new = GpuGridGaussian(test_tile, self.size, sigma)
        self.new.compute_grid()
        self.old = GpuGaussianOld(test_tile.get_Data()[0].getDataSet(), test_tile.get_View().view(), self.size, sigma)
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


class TestGpuGridGaussianCompute_32x32(TestCase):
    def setUp(self):
        self.grid_size = getDimensions(self)
        a = np.array([[3, 3], [5, 5], [3, 5], [5, 3], [4, 4]]).astype(np.float32).reshape(5, 2)
        sigma = .07

        test_set = CellTypeDataSet("", a, rgb=(0, .5, .5))

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


class TestGpuGridGaussianCompute_64x64(TestCase):
    def setUp(self):
        self.grid_size = getDimensions(self)
        a = np.array([[3, 3], [5, 5], [3, 5], [5, 3], [4, 4]]).astype(np.float32).reshape(5, 2)
        self.sigma = .1

        test_set = CellTypeDataSet("", a, rgb=(0, .5, .5))

        # These are the individual tiles that will have information about the dataset
        test_tile = ViewTile((test_set,), (3, 5, 3, 5))

        self.new = GpuGridGaussian(test_tile, self.grid_size, self.sigma)
        self.new.compute_grid()

    def doCleanups(self):
        self.new.clean_cuda()

    def test_shape(self):
        print self.new.get_grid_data()
        new_data = self.new.get_grid_data()
        new_data.shape == self.grid_size

    def test_max_point_value(self):
        g = gaussian_normal_sigma(self.sigma)
        new_data = self.new.get_grid_data()
        diff = math.fabs(new_data.max() - g)
        assert diff < .00001

    def test_min_point_value(self):
        new_data = self.new.get_grid_data()
        assert new_data.min() < .001


class TestGpuGridGaussianComputeComplex_64x64(TestCase):
    def setUp(self):
        self.grid_size = getDimensions(self)
        a = np.array([[3, 3], [5, 5], [3, 5], [5, 3], [4.1, 4.1]]).astype(np.float32).reshape(5, 2)
        self.sigma = .1

        test_set = CellTypeDataSet("", a, rgb=(0, .5, .5))

        # These are the individual tiles that will have information about the dataset
        test_tile = ViewTile((test_set,), (3, 5, 3, 5))

        self.new = GpuGridGaussian(test_tile, self.grid_size, self.sigma)
        self.new.compute_grid()

    def doCleanups(self):
        self.new.clean_cuda()

    def test_max_point_value(self):
        g = gaussian_normal_sigma(self.sigma)
        new_data = self.new.get_grid_data()
        diff = math.fabs(new_data.max() - g)
        assert diff < .00001

    def test_min_point_value(self):
        new_data = self.new.get_grid_data()
        assert new_data.min() < .001

    def test_shape(self):
        new_data = self.new.get_grid_data()
        assert new_data.shape == self.grid_size


class TestGpuGridGaussianComputeComplex_128x128(TestCase):
    def setUp(self):
        self.grid_size = getDimensions(self)
        a = np.array([[3, 3], [5, 5], [3, 5], [5, 3], [4.1, 4.1]]).astype(np.float32).reshape(5, 2)
        self.sigma = .1

        test_set = CellTypeDataSet("", a, rgb=(0, .5, .5))

        # These are the individual tiles that will have information about the dataset
        test_tile = ViewTile((test_set,), (3, 5, 3, 5))

        self.new = GpuGridGaussian(test_tile, self.grid_size, self.sigma)
        self.new.compute_grid()

    def doCleanups(self):
        self.new.clean_cuda()

    def test_max_point_value(self):
        g = gaussian_normal_sigma(self.sigma)
        new_data = self.new.get_grid_data()
        diff = math.fabs(new_data.max() - g)
        assert diff < .00001

    def test_min_point_value(self):
        new_data = self.new.get_grid_data()
        assert new_data.min() < .001

    def test_shape(self):
        new_data = self.new.get_grid_data()
        assert new_data.shape == self.grid_size


class TestGpuGridGaussianComputeComplex_256x256(TestCase):
    def setUp(self):
        self.grid_size = getDimensions(self)
        a = np.array([[3, 3], [5, 5], [3, 5], [5, 3], [4.1, 4.1]]).astype(np.float32).reshape(5, 2)
        self.sigma = .1

        test_set = CellTypeDataSet("", a, rgb=(0, .5, .5))

        # These are the individual tiles that will have information about the dataset
        test_tile = ViewTile((test_set,), (3, 5, 3, 5))

        self.new = GpuGridGaussian(test_tile, self.grid_size, self.sigma)
        self.new.compute_grid()

    def doCleanups(self):
        self.new.clean_cuda()

    def test_shape(self):
        new_data = self.new.get_grid_data()
        assert new_data.shape == self.grid_size

    def test_max_point_value(self):
        g = gaussian_normal_sigma(self.sigma)
        new_data = self.new.get_grid_data()
        diff = math.fabs(new_data.max() - g)
        assert diff < .00001

    def test_min_point_value(self):
        new_data = self.new.get_grid_data()
        assert new_data.min() < .001


class TestGpuGridGaussianComputeComplex_512x512(TestCase):
    def setUp(self):
        self.grid_size = getDimensions(self)
        a = np.array([[3, 3], [5, 5], [3, 5], [5, 3], [4.1, 4.1]]).astype(np.float32).reshape(5, 2)
        self.sigma = .1

        test_set = CellTypeDataSet("", a, rgb=(0, .5, .5))

        # These are the individual tiles that will have information about the dataset
        test_tile = ViewTile((test_set,), (3, 5, 3, 5))

        self.new = GpuGridGaussian(test_tile, self.grid_size, self.sigma)
        self.new.compute_grid()

    def doCleanups(self):
        self.new.clean_cuda()

    def test_shape(self):
        new_data = self.new.get_grid_data()
        assert new_data.shape == self.grid_size

    def test_max_point_value(self):
        g = gaussian_normal_sigma(self.sigma)
        new_data = self.new.get_grid_data()
        diff = math.fabs(new_data.max() - g)
        assert diff < .00001

    def test_min_point_value(self):
        new_data = self.new.get_grid_data()
        assert new_data.min() < .001

"""
class TestGpuGridGaussianActualDataSetBC(TestCase):
    def setUp(self):
        tstart = 0
        tstop = 1500
        numCells = (6600, 4600, 100000, 1000)    # (number of MEA, number of LEA)
        bc_data = ParseParallelCellData(numCells, tstart, tstop, use_cache_data=True).get_bc_data()

        self.grid_size = (64, 2048)
        sigma = .004

        test_set = CellTypeDataSet("", bc_data, rgb=(0, .5, .5))

        # These are the individual tiles that will have information about the dataset
        test_tile = ViewTile((test_set,), (tstart, tstop, 0, 10))

        self.new = GpuGridGaussian(test_tile, self.grid_size, sigma)
        self.new.compute_grid()

    def doCleanups(self):
        self.new.clean_cuda()

    def test_view_data(self):
        self.new.show_image()
"""

class TestGpuGridGaussianComputeComplex_1024x1024(TestCase):
    def setUp(self):
        self.grid_size = getDimensions(self)

        a = np.array([[3, 3], [5, 5], [3, 5], [5, 3], [4.1, 4.1], [3, 3]]).astype(np.float32).reshape(6, 2)
        self.sigma = .1

        test_set = CellTypeDataSet("", a, rgb=(0, .5, .5))

        # These are the individual tiles that will have information about the dataset
        test_tile = ViewTile((test_set,), (3, 5, 3, 5))

        self.new = GpuGridGaussian(test_tile, self.grid_size, self.sigma)
        self.new.compute_grid()

    def doCleanups(self):
        self.new.clean_cuda()

    def test_shape(self):
        new_data = self.new.get_grid_data()
        assert new_data.shape == self.grid_size

    def test_max_point_value(self):
        g = gaussian_normal_sigma(self.sigma) * 2
        new_data = self.new.get_grid_data()
        diff = math.fabs(new_data.max() - g)
        assert diff < .00001

    def test_min_point_value(self):
        new_data = self.new.get_grid_data()
        assert new_data.min() < .001


class TestRandomGpuGridGaussianComputeComplex_1024x1024(TestCase):
    def setUp(self):
        self.grid_size = getDimensions(self)

        a = np.array(np.random.random(400)).astype(np.float32).reshape(200, 2)
        self.sigma = .1

        test_set = CellTypeDataSet("", a, rgb=(0, .5, .5))

        # These are the individual tiles that will have information about the dataset
        test_tile = ViewTile((test_set,), (0, 1, 0, 1))

        self.new = GpuGridGaussian(test_tile, self.grid_size, self.sigma)
        self.new.compute_grid()

    def doCleanups(self):
        self.new.clean_cuda()

    def test_shape(self):
        new_data = self.new.get_grid_data()
        assert new_data.shape == self.grid_size

    def test_max_greater_than(self):
        new_data = self.new.get_grid_data()
        assert new_data.max() > gaussian_normal_sigma(self.sigma)

    def test_min_greater_than(self):
        new_data = self.new.get_grid_data()
        assert new_data.min() > gaussian_normal_sigma(self.sigma)


class TestGpuGridGaussianStudyWindowSize(TestCase):
    def setUp(self):
        a = np.array([[750, 5], [0, 0], [1500, 0], [1500, 10], [0, 10], [237, 2], [237, 2], [1234, 7], [400, 3]]).astype(np.float32).reshape(9, 2)
        self.grid_size = (1024, 1024)
        self.sigma = .1

        test_set = CellTypeDataSet("", a, rgb=(0, .5, .5))

        # These are the individual tiles that will have information about the dataset
        test_tile = ViewTile((test_set,), (0, 1500, 0, 10))

        self.new = GpuGridGaussian(test_tile, self.grid_size, self.sigma)
        self.new.compute_grid()

    def doCleanups(self):
        self.new.clean_cuda()

    def test_shape(self):
        new_data = self.new.get_grid_data()
        assert new_data.shape == self.grid_size

    def test_max_point_value(self):
        g = gaussian_normal_sigma(self.sigma) * 2.425
        new_data = self.new.get_grid_data()
        diff = math.fabs(new_data.max() - g)
        print diff
        assert diff < .1

    def test_min_point_value(self):
        new_data = self.new.get_grid_data()
        assert new_data.min() < .001