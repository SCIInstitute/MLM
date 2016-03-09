# Import data from sharedData.pickle and spikeTimes #
import cPickle
import sys
import numpy as np

from plotDftParameters import *


def dump(obj, nested_level=0, output=sys.stdout):
    """
    @param obj: is the input object where you want to dump
    @param nested_level:
    @param output: read-friendly output of dictionary
    @return:
    credit goes to http://stackoverflow.com/questions/15785719/how-to-print-a-dictionary-line-by-line-in-python
    """
    spacing = '   '
    if type(obj) == dict:
        print >> output, '%s{' % ((nested_level) * spacing)
        for k, v in obj.items():
            if hasattr(v, '__iter__'):
                print >> output, '%s%s:' % ((nested_level + 1) * spacing, k)
                dump(v, nested_level + 1, output)
            else:
                print >> output, '%s%s: %s' % ((nested_level + 1) * spacing, k, v)
        print >> output, '%s}' % (nested_level * spacing)
    elif type(obj) == list:
        print >> output, '%s[' % ((nested_level) * spacing)
        for v in obj:
            if hasattr(v, '__iter__'):
                dump(v, nested_level + 1, output)
            else:
                print >> output, '%s%s' % ((nested_level + 1) * spacing, v)
        print >> output, '%s]' % ((nested_level) * spacing)
    else:
        print >> output, '%s%s' % (nested_level * spacing, obj)


fileName = "spikeTimes"
fileSep = fileName.split('.')
DG_length = 10

f = open(fileName,'r')
spikeData = cPickle.load(f)
f.close()

# Load in locations of the cells
f = open("sharedData.pickle")
combinedData = []
combinedData = cPickle.load(f)
places = combinedData[0]
MEACenters = combinedData[2]
LEACenters = combinedData[3]
BCLocs = combinedData[1]


dump(places[18929])
dump(spikeData[18929])


dump(BCLocs[111200])
dump(spikeData[111200])

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
Basket_pos = []
Basket_pos_t = []
BC_xpos = []


for ii in spikeData.keys():
    if ii < numCells[0]:
        if (ii % 1) == 0:
            for jj in range(len(spikeData[ii])):
                if tstart <= spikeData[ii][jj] <= tstop:
                    # print(ii) range from 0 - 6599
                    MEA.append(ii)
                    #print(spikeData[ii][jj])
                    MEA_t.append(spikeData[ii][jj])
    elif numCells[0] <= ii < numCells[0]+numCells[1]:
        if (ii % 1) == 0:
            for jj in range(len(spikeData[ii])):
                if tstart <= spikeData[ii][jj] <= tstop:
                    #print(ii) range from 6600 - 11199
                    LEA.append(ii)
                    #print(spikeData[ii][jj])
                    LEA_t.append(spikeData[ii][jj])
    elif numCells[0]+numCells[1] <= ii < sum(numCells)+N_GC:
        if (ii % 1) == 0:
            for jj in range(len(spikeData[ii])):
                if tstart <= spikeData[ii][jj] <= tstop:
                    #print(ii) #range from 0 to 111199
                    GC.append(ii)
                    GC_t.append(spikeData[ii][jj])
                    GC_pos_t.append(spikeData[ii][jj])
                    GC_pos.append(places[ii][1])
                    GC_xpos.append(places[ii][0])
                    #print(ii, spikeData[ii][jj], places[ii][1], places[ii][0])
                    #print(np.array([places[ii][0], places[ii][1]], dtype=np.float32).transpose())
    elif ii >= sum(numCells)+N_GC:
        if (ii % 1) == 0:
            for jj in range(len(spikeData[ii])):
                if tstart <= spikeData[ii][jj] <= tstop:
                    BC.append(ii)
                    BC_t.append(spikeData[ii][jj])
                    Basket_pos_t.append(spikeData[ii][jj])
                    Basket_pos.append(BCLocs[ii][1])
                    BC_xpos.append(BCLocs[ii][0])




'''f = open(fileName,'r')
t = []
cID = []
numErrors = 0
errorLines = []
errorCache = []
data = f.readlines() # You now have a list who's elements are each line from the file
f.close()
for i in range(len(data)):
    if len(data[i].split()) != 2:
        errorLines.append(i)
        errorCache.append(data[i])
        numErrors += 1
errorLines.reverse()
for i in errorLines:
    data.pop(i)
errorLines = []
t = [0.0 for i in range(len(data))]
cID = [0 for i in range(len(data))]
for i in range(len(data)):
    line = data[i].split()
    try:
        t[i] = float(line[0])
        cID[i] = int(line[1])
    except ValueError:
        numErrors += 1
        errorLines.append(i)
        errorCache.append(data[i])
    if t[i] > tstop:
        numErrors += 1
        errorLines.append(i)
        errorCache.append(data[i])
    if cID[i] > numGC+numMEA+numLEA+numBC:
        numErrors += 1
        errorLines.append(i)
        errorCache.append(data[i])
errorLines.reverse()
for i in errorLines:
    t.pop(i)
    cID.pop(i)
    data.pop(i)

# Write clean data to new file
f = open(fileSep[0]+".data",'w')
f.writelines(data)
f.close()

# Write all non-data to new file
errorCache.append("\n"+ str(len(t)) + " total lines of data read.\n")
errorCache.append(str(numErrors) + " errors found in file, and not included in plot.\n")
f = open(fileSep[0]+".log",'w')
f.writelines(errorCache)
f.close()

#Now that we're done with the original data and the list of errors, delete them to free up memory!
del data, errorCache

print str(len(t)) + " total lines of data read."
print str(numErrors) + " errors found in file, and not included in plot."

MEA = []
MEA_t = []
LEA = []
LEA_t = []
GC = []
GC_t = []
BC = []
BC_t = []

for ii in range(len(cID)):
    #if (cID[ii] % 2) == 0:
    if cID[ii] < numMEA:
        MEA.append(cID[ii])
        MEA_t.append(t[ii])
    elif numMEA <= cID[ii] < numMEA+numLEA:
        LEA.append(cID[ii])
        LEA_t.append(t[ii])
    elif numMEA+numLEA <= cID[ii] < numMEA+numLEA+numGC:
        GC.append(cID[ii])
        GC_t.append(t[ii])
    elif cID[ii] >= numMEA+numLEA+numGC:
        BC.append(cID[ii])
        BC_t.append(t[ii])

# Load in locations of the granule cells
#f = open('granuleCellLocs','r')
#data = f.readline().split()
#places = {}
#index = 0
#while data:
#	places[int(data[0])] = [float(data[1]), float(data[2])]
#	data = f.readline().split()
#	index += 1
#
#f.close()

f = open("sharedData.pickle")
combinedData = []
combinedData = pickle.load(f)
places = combinedData[0]
MEACenters = combinedData[2]
LEACenters = combinedData[3]
BCLocs = combinedData[1]

GC_pos = []
GC_x = []
GC_pos_t = []
GC_xpos = []
MEA_pos = []
MEA_pos_t = []
LEA_pos = []
LEA_pos_t = []
Basket_pos = []
Basket_pos_t = []
for ii in range(len(cID)):
    if numMEA+numLEA <= cID[ii] < numMEA+numLEA+numGC:
        GC_pos.append(places[cID[ii]][1])
        GC_x.append(places[cID[ii]][0])
        GC_pos_t.append(t[ii])
    elif cID[ii] < numMEA:
        MEA_pos.append(MEACenters[cID[ii]])
        MEA_pos_t.append(t[ii])
    elif numMEA <= cID[ii] < numMEA+numLEA:
        LEA_pos.append(LEACenters[cID[ii]])
        LEA_pos_t.append(t[ii])
    else:
        Basket_pos.append(BCLocs[cID[ii]][1])
        Basket_pos_t.append(t[ii])

# These data files are huge!  Delete anything we don't need!
del t, cID
'''
