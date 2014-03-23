from unittest import TestCase
from dev.gaussian_cpu import CpuGridGaussian
from dev.gaussian_gpu_grid import GpuGridGaussian
from gaussian_gpu import GpuGaussianOld
import numpy as np
from models import CellTypeDataSet, ParseParallelCellData
from view import ViewTile

__author__ = 'mavinm'
__date__ = '3/22/14'


class TestGpuGridGaussianNoCompute(TestCase):
    def setUp(self):
        a = np.array([[0, 0], [1, 1], [0, 1], [1, 0], [.5, .5]]).astype(np.float32).reshape(5, 2)

        test_set = CellTypeDataSet("GC Cell Septotemporal Position (mm)", a, rgb=(0, .5, .5))

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

        test_set = CellTypeDataSet("GC Cell Septotemporal Position (mm)", a, rgb=(0, .5, .5))

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


class TestGpuGridGaussianCompute32x32(TestCase):
    def setUp(self):
        a = np.array([[3, 3], [5, 5], [3, 5], [5, 3], [4, 4]]).astype(np.float32).reshape(5, 2)
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
        sigma = .07

        test_set = CellTypeDataSet("GC Cell Septotemporal Position (mm)", a, rgb=(0, .5, .5))

        # These are the individual tiles that will have information about the dataset
        test_tile = ViewTile((test_set,), (3, 5, 3, 5))

        self.new = GpuGridGaussian(test_tile, self.grid_size, sigma, debug=True)
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


class TestGpuGridGaussianComputeComplex128x128(TestCase):
    def setUp(self):
        a = np.array([[3, 3], [5, 5], [3, 5], [5, 3], [4.1, 4.1]]).astype(np.float32).reshape(5, 2)
        self.grid_size = (128, 128)
        sigma = .4

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

    def test_alike_arrays(self):
        new_data = self.new.get_grid_data()
        old_data = self.old.get_grid_data()
        assert np.allclose(new_data, old_data)

    def test_size(self):
        new_data = self.new.get_grid_data()
        assert new_data.shape == self.grid_size


class TestGpuGridGaussianComputeComplex256x256(TestCase):
    def setUp(self):
        a = np.array([[3, 3], [5, 5], [3, 5], [5, 3], [4.1, 4.1]]).astype(np.float32).reshape(5, 2)
        self.grid_size = (256, 256)
        sigma = .4

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

    def test_alike_arrays(self):
        new_data = self.new.get_grid_data()
        old_data = self.old.get_grid_data()
        assert np.allclose(new_data, old_data)

    def test_size(self):
        new_data = self.new.get_grid_data()
        assert new_data.shape == self.grid_size


class TestGpuGridGaussianComputeComplex512x512(TestCase):
    def setUp(self):
        a = np.array([[3, 3], [5, 5], [3, 5], [5, 3], [4.1, 4.1]]).astype(np.float32).reshape(5, 2)
        self.grid_size = (512, 512)
        sigma = .4

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

    def test_alike_arrays(self):
        new_data = self.new.get_grid_data()
        old_data = self.old.get_grid_data()
        assert np.allclose(new_data, old_data)

    def test_size(self):
        new_data = self.new.get_grid_data()
        assert new_data.shape == self.grid_size


class TestGpuGridGaussianComputeComplex1024x1024(TestCase):
    def setUp(self):
        a = np.array([[3, 3], [5, 5], [3, 5], [5, 3], [4.1, 4.1], [3, 3]]).astype(np.float32).reshape(6, 2)
        self.grid_size = (1024, 1024)
        sigma = .001

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

    def test_alike_arrays(self):
        new_data = self.new.get_grid_data()
        old_data = self.old.get_grid_data()
        assert np.allclose(new_data, old_data)

    def test_size(self):
        new_data = self.new.get_grid_data()
        assert new_data.shape == self.grid_size


class TestRandomGpuGridGaussianComputeComplex1024x1024(TestCase):
    def setUp(self):
        a = np.array(np.random.random(12)).astype(np.float32).reshape(6, 2)
        self.grid_size = (1024, 1024)
        sigma = .0005

        test_set = CellTypeDataSet("GC Cell Septotemporal Position (mm)", a, rgb=(0, .5, .5))

        # These are the individual tiles that will have information about the dataset
        test_tile = ViewTile((test_set,), (0, 1, 0, 1))

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

    def test_alike_arrays(self):
        new_data = self.new.get_grid_data()
        old_data = self.old.get_grid_data()
        assert np.allclose(new_data, old_data)

    def test_size(self):
        new_data = self.new.get_grid_data()
        assert new_data.shape == self.grid_size


class TestGpuGridGaussianStudyWindowSize(TestCase):
    def setUp(self):
        a = np.array([[750, 5], [0, 0], [1500, 0], [1500, 10], [0, 10], [237, 2], [237, 2], [1234, 7], [400, 3]]).astype(np.float32).reshape(9, 2)
        self.grid_size = (1024, 1024)
        sigma = .001

        test_set = CellTypeDataSet("GC Cell Septotemporal Position (mm)", a, rgb=(0, .5, .5))

        # These are the individual tiles that will have information about the dataset
        test_tile = ViewTile((test_set,), (0, 1500, 0, 10))

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

    def test_alike_arrays(self):
        new_data = self.new.get_grid_data()
        old_data = self.old.get_grid_data()
        assert np.allclose(new_data, old_data)

    def test_size(self):
        new_data = self.new.get_grid_data()
        assert new_data.shape == self.grid_size


class TestGpuGridGaussianActualDataSetMeaLea(TestCase):
    def setUp(self):
        tstart = 0
        tstop = 1500
        numCells = (6600, 4600, 100000, 1000)    # (number of MEA, number of LEA)
        mea_data = ParseParallelCellData(numCells, tstart, tstop, use_cache_data=True).get_mea_data()
        lea_data = ParseParallelCellData(numCells, tstart, tstop, use_cache_data=True).get_lea_data()

        self.grid_size = (1024, 1024)
        sigma = .002

        mea_set = CellTypeDataSet("MEA", mea_data, rgb=(0, .5, .5))
        lea_set = CellTypeDataSet("LEA", lea_data, rgb=(0, .5, .5))

        # These are the individual tiles that will have information about the dataset
        test_tile = ViewTile((mea_set, lea_set,), (tstart, tstop, 0, sum(numCells[0:2])))

        self.new = GpuGridGaussian(test_tile, self.grid_size, sigma)
        self.new.compute_grid()

    def doCleanups(self):
        self.new.clean_cuda()

    def test_view_data(self):
        self.new.show_image()

"""
class TestGpuGridGaussianActualDataSetBC(TestCase):
    def setUp(self):
        tstart = 0
        tstop = 1500
        numCells = (6600, 4600, 100000, 1000)    # (number of MEA, number of LEA)
        bc_data = ParseParallelCellData(numCells, tstart, tstop, use_cache_data=True).get_bc_data()

        self.grid_size = (1024, 1024)
        sigma = .002

        test_set = CellTypeDataSet("GC Cell Septotemporal Position (mm)", bc_data, rgb=(0, .5, .5))

        # These are the individual tiles that will have information about the dataset
        test_tile = ViewTile((test_set,), (tstart, tstop, 0, 10))

        self.new = GpuGridGaussian(test_tile, self.grid_size, sigma)
        self.new.compute_grid()

    def doCleanups(self):
        self.new.clean_cuda()

    def test_view_data(self):
        self.new.show_image()


class TestGpuGridGaussianActualDataSetGC(TestCase):
    def setUp(self):
        tstart = 0
        tstop = 1500
        numCells = (6600, 4600, 100000, 1000)    # (number of MEA, number of LEA)
        gc_data = ParseParallelCellData(numCells, tstart, tstop, use_cache_data=True).get_gc_data()

        self.grid_size = (1024, 1024)
        sigma = .001

        test_set = CellTypeDataSet("GC Cell Septotemporal Position (mm)", gc_data, rgb=(0, .5, .5))

        # These are the individual tiles that will have information about the dataset
        test_tile = ViewTile((test_set,), (tstart, tstop, 0, 10))

        self.new = GpuGridGaussian(test_tile, self.grid_size, sigma)
        self.new.compute_grid()

    def doCleanups(self):
        self.new.clean_cuda()

    def test_view_data(self):
        self.new.show_image()
"""

class TestGpuGridGaussianCompute128x128(TestCase):
    def setUp(self):
        a = np.array([[0, 0], [1, 1], [0, 1], [1, 0], [.5, .5]]).astype(np.float32).reshape(5, 2)
        self.size = (128, 128)
        sigma = .035

        test_set = CellTypeDataSet("GC Cell Septotemporal Position (mm)", a, rgb=(0, .5, .5))

        # These are the individual tiles that will have information about the dataset
        test_tile = ViewTile((test_set,), (0, 1, 0, 1))

        self.new = GpuGridGaussian(test_tile, self.size, sigma)
        self.new.compute_grid()
        self.old = GpuGaussianOld(test_tile.get_Data()[0].getDataSet(), test_tile.get_View().view(), self.size, sigma)
        self.old.compute_grid()

    def doCleanups(self):
        self.new.clean_cuda()
        self.old.clean_cuda()

    def test_shape(self):
        new_data = self.new.get_grid_data()
        old_data = self.old.get_grid_data()
        assert new_data.shape == old_data.shape

    def test_alike_arrays(self):
        new_data = self.new.get_grid_data()
        old_data = self.old.get_grid_data()
        assert np.allclose(new_data, old_data)

    def test_size(self):
        new_data = self.new.get_grid_data()
        assert new_data.shape == self.size


class TestGpu2Cpu(TestCase):
    def setUp(self):
        a = np.array([[0, 0], [1, 1], [0, 1], [1, 0], [.5, .5]]).astype(np.float32).reshape(5, 2)
        self.size = (64, 64)
        sigma = .07

        test_set = CellTypeDataSet("GC Cell Septotemporal Position (mm)", a, rgb=(0, .5, .5))

        # These are the individual tiles that will have information about the dataset
        test_tile = ViewTile((test_set,), (0, 1, 0, 1))

        self.gpu = GpuGridGaussian(test_tile, self.size, sigma)
        self.gpu.compute_grid()
        self.cpu = CpuGridGaussian(test_tile.get_Data()[0].getDataSet(), test_tile.get_View().view(), self.size, sigma)

    def doCleanups(self):
        self.gpu.clean_cuda()

    def test_size(self):
        assert self.cpu.pixels.shape == self.gpu.get_grid_data().shape

    def test_equal_arrays(self):
        assert np.allclose(self.cpu.pixels, self.gpu.get_grid_data())

    def test_equiv_arrays(self):
        assert np.allclose(self.cpu.pixels, self.gpu.get_grid_data())