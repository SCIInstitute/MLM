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

my_marker_size = 2

N_GC = 100000        # Number of granule cells
numCells = (6600, 4600)    # (number of MEA, number of LEA)
nBasketCells = 1000
tstart = 0
tstop = 1500

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

f = open("GC.csv", "w")
f.write("cell,pos_x,pos_y\n")

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

print str(len(MEA)) + " MEA spikes,"
print str(len(LEA)) + " LEA spikes,"
print str(len(GC)) + " Granule cell spikes, and"
print str(len(BC)) + " Basket cell spikes."

f.close()

MEA_results = np.array([MEA_t, MEA], dtype=np.float32).transpose()
LEA_results = np.array([LEA_t, LEA], dtype=np.float32).transpose()

app = QtGui.QApplication(sys.argv)
# Plot MEA
window = MEA_LEA_Window(MEA_results, LEA_results, tstart, tstop, 0, sum(numCells))
window.show()
app.exec_()

#### CONVERTING TO OPEN GL
# fig = plt.figure(2, figsize=(24, 15))
# plt.subplots_adjust(left=0.04, right=0.99, bottom=0.05, top=0.99)
# plt.subplot2grid((7, 1), (1, 0), rowspan=4, picker=5)
# plt.plot(GC_t, GC_pos, '.k', markersize=my_marker_size)
# plt.ylabel("GC Cell Septotemporal Position (mm)")
# plt.xlim((tstart, tstop))
#
# plt.subplot2grid((7, 1), (0, 0))
# plt.plot(BC_t, BC_pos, '.m', markersize=my_marker_size, picker=5)
# plt.ylabel("Basket Cells")
# plt.xlim((tstart, tstop))
#
# plt.subplot2grid((7, 1), (5, 0), rowspan=2)
# plt.ylabel(
#     "Cell # (MEA = 0 - %i," % (numCells[0] - 1) + " LEA = %i" % numCells[0] + " - %i" % (numCells[0] + numCells[1] - 1))
# plt.xlabel("Time (ms)")
# plt.xlim((tstart, tstop))
# plt.ylim((0, sum(numCells)))
