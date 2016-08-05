from PyQt4.QtCore import QTimer
from PyQt4.QtGui import QApplication
import signal

# My Parameters
import sys
import models
from settings import USE_CACHING
from widget import GuiCellPlot, UIWidget
from view import ViewTile

signal.signal(signal.SIGINT, signal.SIG_DFL)
isRegression = sys.argv[-1] == "--regression"

my_marker_size = 2

N_GC = 100000        # Number of granule cells
numCells = (6600, 4600, 100000, 1000)    # (number of MEA, number of LEA)
tstart = 0
tstop = 1500

data = models.ParseParallelCellData(numCells, tstart, tstop, use_cache_data=USE_CACHING)
mea_data, lea_data, gc_data, bc_data = data.get_data()

print str(mea_data.shape[0]) + " MEA spikes,"
print str(lea_data.shape[0]) + " LEA spikes,"
print str(gc_data.shape[0]) + " Granule cell spikes, and"
print str(bc_data.shape[0]) + " Basket cell spikes."

# Create an PyQT4 application object.
app = QApplication(sys.argv)

mea_set = models.CellTypeDataSet("Cell # \n(MEA 0 - 6599, ", mea_data, rgb=(0, 0, .5))
lea_set = models.CellTypeDataSet("\nLEA 660 - 11199)", lea_data, rgb=(.5, 0, 0))
gc_set = models.CellTypeDataSet("GC Cell Septotemporal Position (mm)", gc_data, rgb=(0, .5, .5))
bc_set = models.CellTypeDataSet("Basket Cells", bc_data, rgb=(.5, 0, .5))


# These are the individual tiles that will have information about the dataset
mea_lea_tile = ViewTile((mea_set, lea_set), (tstart, tstop, 0, sum(numCells[0:2])))
gc_tile = ViewTile((gc_set,), (tstart, tstop, 0, 10))
bc_tile = ViewTile((bc_set,), (tstart, tstop, 0, 10))

# g = GridGaussian(bc_data, bc_tile.get_View().view(), (100, 100), 1)
# g.save_image()
# print "Completed showing data now"

# should have one window, but three GuiCellPlots in it, or
# have GuiCellPlot be a singleton class with substructures for each plot
window = GuiCellPlot(mea_lea_tile, gc_tile, bc_tile, cell_hierarchy=data.cell_hierarchy)

ui_widget = UIWidget(window)
window.set_ui_heightmap_widget(ui_widget)
window.show()

sys.exit(app.exec_())
