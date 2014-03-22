from gaussian_gpu import GpuGridGaussian
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

    sigma = .2
    for i in range(1, 6):
        g = GpuGridGaussian(bc_data, bc_tile.get_View().orig_view, (1024, 1024), i*sigma)
        g.save_image("tmp/bc_data_gaussian_sigma=" + str(i*sigma) + ".bin")
        g.clean_cuda()