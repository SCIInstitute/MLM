import cPickle
import pickle
import pylab as plt
from tools import ToolQB
from data.simulationParameters import *

class plotSingleCellDetails:
    """
    Plots the single cell from the rasterized layout and shows all driver cells
    """

    mymarkersize = 6

    def __init__(self, tstart, tstop):
        dir = "data"
        imageName = "./" + dir + "/VoltageTrace_GC.png"
        fileName = "./" + dir + "/spikeTimes"
        cellVoltDataFile = "./" + dir + "/voltageTraces/granuleCells_CPU0.out"

        f = open(fileName, 'r')
        spikeData = cPickle.load(f)
        f.close()

        # Get voltage and connectivity information for the cell
        f = open(cellVoltDataFile)
        cellInfo = cPickle.load(f)
        f.close()

        self.cellSomaT = cellInfo[0][6][0] # This is the global time vector/list for the cell
        self.cellSomaV = cellInfo[0][6][1][0] # The first voltage recording will be at the soma


        #Then, get the connectivity information for that cell
        cellConnData = cellInfo[0][5].keys()
        cellConnData.sort()
        cellConnData.reverse()
        print cellConnData[0:9]
        # Then, pull the spike info for ONLY the cells that synapse onto the target cell.


        f = open("./" + dir + "/sharedData.pickle")
        combinedData = []
        combinedData = pickle.load(f)
        places = combinedData[0]
        BCLocs = combinedData[1]
        MEACenters = combinedData[2]
        LEACenters = combinedData[3]

        self.MEA = []
        self.MEA_t = []
        self.LEA = []
        self.LEA_t = []
        GC = []
        self.GC_t = []
        BC = []
        self.BC_t = []
        self.GC_pos = []
        GC_xpos = []
        self.BC_pos = []
        BC_xpos = []

        missingCells = []
        for ii in cellConnData:
            try:
                if ii < numCells[0]:
                    if (ii % 1) == 0:
                        for jj in range(len(spikeData[ii])):
                            if tstart <= spikeData[ii][jj] <= tstop:
                                self.MEA.append(self.calculateYPosition(ii, numCells[0], 0, -52, -48))
                                self.MEA_t.append(spikeData[ii][jj])
                elif numCells[0] <= ii < numCells[0] + numCells[1]:
                    if (ii % 1) == 0:
                        for jj in range(len(spikeData[ii])):
                            if tstart <= spikeData[ii][jj] <= tstop:
                                self.LEA.append(self.calculateYPosition(ii, numCells[1], numCells[0], -56, -52))
                                self.LEA_t.append(spikeData[ii][jj])
                elif numCells[0] + numCells[1] <= ii < sum(numCells) + N_GC:
                    if (ii % 1) == 0:
                        for jj in range(len(spikeData[ii])):
                            if tstart <= spikeData[ii][jj] <= tstop:
                                self.GC_t.append(spikeData[ii][jj])
                                self.GC_pos.append(self.calculateYPosition(ii, N_GC, sum(numCells), -64, -56))
                elif ii >= sum(numCells) + N_GC:
                    if (ii % 1) == 0:
                        for jj in range(len(spikeData[ii])):
                            if tstart <= spikeData[ii][jj] <= tstop:
                                self.BC_t.append(spikeData[ii][jj])
                                self.BC_pos.append(self.calculateYPosition(ii, numBasketCells, sum(numCells) + N_GC, -69, -64))
            except KeyError:
                missingCells.append(ii)
        print str(len(missingCells)) + " input cells, out of " + str(
            len(cellConnData)) + ", didn't generate any spikes (or you have an error in your main simulation code)."
        print "missingCells: " + str(missingCells)
        self.plot_figure()

    def plot_figure(self):
        plt.figure(2, figsize=(24, 15))
        plt.subplots_adjust(left=0.04, right=0.99, bottom=0.04, top=0.97)
        # Black
        plt.plot(self.cellSomaT, self.cellSomaV, 'k', markersize=6)
        # Blue
        plt.plot(self.MEA_t, self.MEA, '.b', markersize=self.mymarkersize)
        # Red
        plt.plot(self.LEA_t, self.LEA, '.r', markersize=self.mymarkersize)
        # Black
        plt.plot(self.GC_t, self.GC_pos, '.k', markersize=self.mymarkersize)
        # Magenta
        plt.plot(self.BC_t, self.BC_pos, '.m', markersize=self.mymarkersize)
        plt.xlabel("Time (ms)")
        plt.ylabel("Membrane Voltage (mV) @ soma")
        plt.title("Granule Cell Somal Voltage (with all input from MEA, LEA, and BCs)")
        plt.xlim((tstart, tstop))

        plt.show()

    def calculateYPosition(self, val, numCells, A, C, D):
        return (val - A * 1.0) * (C - D) / numCells + D


if __name__ == '__main__':
    tstart = 0
    tstop = 1500
    plotSingleCellDetails(tstart, tstop)