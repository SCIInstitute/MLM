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


class ParseCellData():
    """
    use_cache_data : If set to true, ignores parsing the file, instead looks on disk for a cached file binary array

    Returns (MEA_data, LEA_data, GC_data, BC_data)
    """
    rendered_file = "parallelData.bin"

    def __init__(self, use_cache_data=False):

        self.mea_data = None
        self.lea_data = None
        self.gc_data = None
        self.bc_data = None

        if use_cache_data:
            self.file_on_disk()
        else:
            self.load_data()

    def file_on_disk(self):
        if not os.path.isfile(self.rendered_file):
            return self.load_data()

        f = file(self.rendered_file, "rb")
        self.mea_data = np.load(f)
        self.lea_data = np.load(f)
        self.gc_data = np.load(f)
        self.bc_data = np.load(f)
        f.close()

    def load_data(self):
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

        self.mea_data = np.array([MEA_t, MEA], dtype=np.float32).transpose()
        self.lea_data = np.array([LEA_t, LEA], dtype=np.float32).transpose()
        self.gc_data = np.array([GC_t, GC_pos], dtype=np.float32).transpose()
        self.bc_data = np.array([BC_t, BC_pos], dtype=np.float32).transpose()

        f = file(self.already_rendered_file, "wb")
        np.save(f, self.mea_data)
        np.save(f, self.lea_data)
        np.save(f, self.gc_data)
        np.save(f, self.bc_data)
        f.close()

    def get_data(self):
        return self.mea_data, self.lea_data, self.gc_data, self.bc_data

data = ParseCellData(use_cache_data=True)
mea_data, lea_data, gc_data, bc_data = data.get_data()

print str(mea_data.shape[0]) + " MEA spikes,"
print str(lea_data.shape[0]) + " LEA spikes,"
print str(gc_data.shape[0]) + " Granule cell spikes, and"
print str(bc_data.shape[0]) + " Basket cell spikes."

app = QtGui.QApplication(sys.argv)

mea_set = CellTypeDataSet(mea_data, rgb=(0, 0, 1))
lea_set = CellTypeDataSet(lea_data, rgb=(1, 0, 0))
gc_set = CellTypeDataSet(gc_data, rgb=(0, 0, 0))
bc_set = CellTypeDataSet(bc_data, rgb=(1, 0, 1))

# These are the individual tiles that will have information about the dataset
mea_lea_tile = WindowTile((mea_set, lea_set), (tstart, tstop, 0, sum(numCells)))
gc_tile = WindowTile((gc_set,), (tstart, tstop, 0, 10))
bc_tile = WindowTile((bc_set,), (tstart, tstop, 0, 10))

window = GuiCellPlot(mea_lea_tile, gc_tile, bc_tile)
window.show()
app.exec_()
