import os
from PyQt4 import QtGui
import pickle
import cPickle
from matplotlib import pyplot as plt
import numpy as np
import numpy.random as rdn

# My Parameters
import sys
from modules import *
from plotSingleCellDetails_newFormat import plotSingleCellDetails
from windows import GuiCellPlot, WindowTile

my_marker_size = 2

N_GC = 100000        # Number of granule cells
numCells = (6600, 4600)    # (number of MEA, number of LEA)
nBasketCells = 1000
tstart = 0
tstop = 1500

already_rendered_file = "parallelData.bin"
if os.path.isfile(already_rendered_file):
    print already_rendered_file + " found, skipping rendering cycle."

    f = file(already_rendered_file, "rb")
    MEA_data = np.load(f)
    LEA_data = np.load(f)
    GC_data = np.load(f)
    BC_data = np.load(f)
    f.close()
else:
    #dataDir = "MEA6600-LEA4600-GC100000-BASKET0-t10000topographic_no-b_AHP_sngl_10-02-2012neg"
    #dataDir = "{6600.4600.100000.1000}-t1500.recurInh_02.03.13-d"
    dataDir = "myData"
    imageName = "./" + dataDir + "/recurInh_i.png"
    fileName = "./" + dataDir + "/spikeTimes"

    f = open(fileName, 'r')
    spikeData = cPickle.load(f)
    f.close()

    # Load in locations of the cells
    f = open("./" + dataDir + "/sharedData.pickle")
    combinedData = []
    combinedData = cPickle.load(f)
    f.close()
    places = combinedData[0]
    MEACenters = combinedData[2]
    LEACenters = combinedData[3]
    BCLocs = combinedData[1]

    MEA = []
    MEA_t = []
    LEA = []
    LEA_t = []
    GC = []
    GC_t = []
    BC = []
    BC_t = []
    GC_pos = []
    GC_pos_t = []
    GC_xpos = []
    BC_pos = []
    BC_pos_t = []
    BC_xpos = []

    for ii in spikeData.keys():
        # Medial Entorhinal Area
        if ii < numCells[0]:
            if (ii % 1) == 0:
                for jj in range(len(spikeData[ii])):
                    if tstart <= spikeData[ii][jj] <= tstop:
                        MEA.append(float(ii))
                        MEA_t.append(float(spikeData[ii][jj]))
        # Lateral Entorhinal Area
        elif numCells[0] <= ii < numCells[0] + numCells[1]:
            if (ii % 1) == 0:
                for jj in range(len(spikeData[ii])):
                    if tstart <= spikeData[ii][jj] <= tstop:
                        LEA.append(ii)
                        LEA_t.append(spikeData[ii][jj])
        # Granule Cell
        elif numCells[0] + numCells[1] <= ii < sum(numCells) + N_GC:
            if (ii % 1) == 0:
                for jj in range(len(spikeData[ii])):
                    if tstart <= spikeData[ii][jj] <= tstop:
                        GC.append(ii)
                        GC_t.append(spikeData[ii][jj])
                        GC_pos.append(places[ii][1])
                        GC_xpos.append(places[ii][0])

        # Basket Cell
        elif ii >= sum(numCells) + N_GC:
            if (ii % 1) == 0:
                for jj in range(len(spikeData[ii])):
                    if tstart <= spikeData[ii][jj] <= tstop:
                        BC.append(ii)
                        BC_t.append(spikeData[ii][jj])
                        BC_pos.append(BCLocs[ii][1])
                        BC_xpos.append(BCLocs[ii][0])

    MEA_data = np.array([MEA_t, MEA], dtype=np.float32).transpose()
    LEA_data = np.array([LEA_t, LEA], dtype=np.float32).transpose()
    GC_data = np.array([GC_t, GC_pos], dtype=np.float32).transpose()
    BC_data = np.array([BC_t, BC_pos], dtype=np.float32).transpose()

    f = file(already_rendered_file, "wb")
    np.save(f, MEA_data)
    np.save(f, LEA_data)
    np.save(f, GC_data)
    np.save(f, BC_data)
    f.close()

print str(MEA_data.shape[0]) + " MEA spikes,"
print str(LEA_data.shape[0]) + " LEA spikes,"
print str(GC_data.shape[0]) + " Granule cell spikes, and"
print str(BC_data.shape[0]) + " Basket cell spikes."

app = QtGui.QApplication(sys.argv)

mea_set = CellTypeDataSet(MEA_data, rgb=(0, 0, 1))
lea_set = CellTypeDataSet(LEA_data, rgb=(1, 0, 0))
gc_set = CellTypeDataSet(GC_data, rgb=(0, 0, 0))
bc_set = CellTypeDataSet(BC_data, rgb=(1, 0, 1))

# These are the individual tiles that will have information about the dataset
mea_lea_tile = WindowTile((mea_set, lea_set), (tstart, tstop, 0, sum(numCells)))
gc_tile = WindowTile((gc_set,), (tstart, tstop, 0, 10))
bc_tile = WindowTile((bc_set,), (tstart, tstop, 0, 10))

window = GuiCellPlot(mea_lea_tile, gc_tile, bc_tile)
window.show()
app.exec_()
