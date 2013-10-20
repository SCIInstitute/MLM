from PyQt4 import QtGui, QtCore

# My Parameters
import sys
from models import *
from plotSingleCellDetails_newFormat import plotSingleCellDetails
from widget import GuiCellPlot
from view import ViewTile

my_marker_size = 2

N_GC = 100000        # Number of granule cells
numCells = (6600, 4600, 100000, 1000)    # (number of MEA, number of LEA)
tstart = 0
tstop = 1500

data = ParseCellData(numCells, tstart, tstop, use_cache_data=True)
mea_data, lea_data, gc_data, bc_data = data.get_data()

print str(mea_data.shape[0]) + " MEA spikes,"
print str(lea_data.shape[0]) + " LEA spikes,"
print str(gc_data.shape[0]) + " Granule cell spikes, and"
print str(bc_data.shape[0]) + " Basket cell spikes."

app = QtGui.QApplication(sys.argv)

mea_set = CellTypeDataSet(mea_data, rgb=(0, 0, .5))
lea_set = CellTypeDataSet(lea_data, rgb=(.5, 0, 0))
gc_set = CellTypeDataSet(gc_data, rgb=(0, .5, .5))
bc_set = CellTypeDataSet(bc_data, rgb=(.5, 0, .5))

# These are the individual tiles that will have information about the dataset
mea_lea_tile = ViewTile("mea_lea", (mea_set, lea_set), (tstart, tstop, 0, sum(numCells[0:2])))
gc_tile = ViewTile("gc", (gc_set,), (tstart, tstop, 0, 10))
bc_tile = ViewTile("bc", (bc_set,), (tstart, tstop, 0, 10))

window = GuiCellPlot(mea_lea_tile, gc_tile, bc_tile)
window.show()

print "Open GL Version: " + gl.glGetString(gl.GL_VERSION)
print "Open GLSL Version: " + gl.glGetString(gl.GL_SHADING_LANGUAGE_VERSION)

app.exec_()
