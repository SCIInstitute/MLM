from plotParallelData_pos_newFormat import *

"""
lea_f = open("LEA.csv", "w")

lea_f.write("Cell,spiketime\n")
for i in range(len(LEA)):
    lea_f.write(str(LEA[i]) + "," + str(LEA_t[i]) + "\n")

lea_f.close()

mea_f = open("MEA.csv", "w")

mea_f.write("Cell,spiketime\n")
for i in range(len(MEA)):
    mea_f.write(str(MEA[i]) + "," + str(MEA_t[i]) + "\n")

mea_f.close()
"""

def writeDataSpikes(filename, data, time):
    f = open(filename, "w")

    f.write("cell,spiketime\n")
    for i in range(len(data)):
        f.write(str(data[i]) + "," + str(time[i]) + "\n")

    f.close()

def writeDataPos(filename, data, pos_x, pos_y):
    f = open(filename, "w")
    f.write("cell,pos_x,pos_y\n")
    cell = None
    for i in range(len(data)):
        if cell == data[i]:
            continue
        cell = data[i]
        f.write(str(cell) + "," + str(pos_x[i]) + "," + str(pos_y[i]) + "\n")

    f.close()


writeDataSpikes("GC.csv", GC, GC_t)
writeDataPos("GC_pos.csv", GC, GC_xpos, GC_pos)

writeDataSpikes("BC.csv", BC, BC_t)
writeDataPos("BC_pos.csv", BC, BC_xpos, BC_pos)