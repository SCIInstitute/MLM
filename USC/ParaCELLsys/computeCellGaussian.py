from gaussian_gpu_grid import GpuGridGaussian
from models import ParseParallelCellData, CellTypeDataSet
from view import ViewTile

__author__ = 'mavinm'
__date__ = '3/21/14'


if __name__ == "__main__":

    N_GC = 100000        # Number of granule cells
    numCells = (6600, 4600, 100000, 1000)    # (number of MEA, number of LEA)
    tstart = 0
    tstop = 1500

    data = ParseParallelCellData(numCells, tstart, tstop, use_cache_data=True)
    mea_data, lea_data, gc_data, bc_data = data.get_data()

    print str(mea_data.shape[0]) + " MEA spikes,"
    print str(lea_data.shape[0]) + " LEA spikes,"
    print str(gc_data.shape[0]) + " Granule cell spikes, and"
    print str(bc_data.shape[0]) + " Basket cell spikes."

    mea_set = CellTypeDataSet("Cell # \n(MEA 0 - 6599, ", mea_data, rgb=(0, 0, .5))
    lea_set = CellTypeDataSet("\nLEA 660 - 11199)", lea_data, rgb=(.5, 0, 0))
    gc_set = CellTypeDataSet("GC Cell Septotemporal Position (mm)", gc_data, rgb=(0, .5, .5))
    bc_set = CellTypeDataSet("Basket Cells", bc_data, rgb=(.5, 0, .5))

    mea_lea_tile = ViewTile((mea_set, lea_set), (tstart, tstop, 0, sum(numCells[0:2])))
    gc_tile = ViewTile((gc_set,), (tstart, tstop, 0, 10))
    bc_tile = ViewTile((bc_set,), (tstart, tstop, 0, 10))

    # Values are normalized from [0-1500, 0-n] to grid of [0-1, 0-1].  Sigma choice should be between 0-1
    sigma = 0.001

    gc = GpuGridGaussian(gc_tile, (1024, 1024), sigma)
    gc.compute_grid()
    gc.save_image("tmp/gc_data_gaussian_sigma=" + str(sigma) + ".bin")
    gc.show_image()
    gc.clean_cuda()

    bc = GpuGridGaussian(bc_tile, (1024, 1024), sigma)
    bc.compute_grid()
    bc.save_image("tmp/bc_data_gaussian_sigma=" + str(sigma) + ".bin")
    bc.show_image()
    bc.clean_cuda()

    mea_lea = GpuGridGaussian(mea_lea_tile, (1024, 1024), sigma)
    mea_lea.compute_grid()
    mea_lea.save_image("tmp/mea_lea_data_gaussian_sigma=" + str(sigma) + ".bin")
    mea_lea.show_image()
    mea_lea.clean_cuda()