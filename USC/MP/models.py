import OpenGL.GL as gl
import OpenGL.arrays.vbo as glvbo
import os
import cPickle, pickle
import numpy as np

__author__ = 'mavinm'


class ParseCellData():
    """
    Parses the dataset given by USC using caching option

    num_cells      : A tuple consisting of the sizes as follows (MEA_size, LEA_size, GC_size, BC_size)
    t_start        : Start time to the spike times
    t_stop         : End time of the spike times
    use_cache_data : If set to true, ignores parsing the file, instead looks on disk for a cached file binary array

    Returns (MEA_data, LEA_data, GC_data, BC_data)
    """

    def __init__(self, num_cells, t_start, t_stop, use_cache_data=False):

        self.mea_data = None
        self.lea_data = None
        self.gc_data = None
        self.bc_data = None

        self.num_cells = num_cells
        self.t_start = t_start
        self.t_stop = t_stop

        if use_cache_data:
            self.file_on_disk()
        else:
            self.load_data()

        self.complete()

    def complete(self):
        """ Used after loading data is complete """
        pass

    def load_data(self):
        raise NotImplemented("This needs to be implemented and you should call self.save() afterwards for caching")

    def save(self):
        # Create directory 'tmp' if it does not exist
        dir = self.rendered_file.split('/')
        if not os.path.exists(dir[-2]):
            os.mkdir(dir[-2])

        f = file(self.rendered_file, "wb")
        # Saves parallel data
        np.save(f, self.mea_data)
        np.save(f, self.lea_data)
        np.save(f, self.gc_data)
        np.save(f, self.bc_data)

        f.close()

    def file_on_disk(self):
        if not os.path.isfile(self.rendered_file):
            return self.load_data()

        f = file(self.rendered_file, "rb")

        self.mea_data = np.load(f)
        self.lea_data = np.load(f)
        self.gc_data = np.load(f)
        self.bc_data = np.load(f)

        f.close()

    def get_data(self):
        return self.mea_data, self.lea_data, self.gc_data, self.bc_data

    def get_mea_data(self):
        return self.mea_data

    def get_lea_data(self):
        return self.lea_data

    def get_gc_data(self):
        return self.gc_data

    def get_bc_data(self):
        return self.bc_data


class ParseParallelCellData(ParseCellData):
    rendered_file = "tmp/parallelData.bin"

    def load_data(self):
        #dataDir = "MEA6600-LEA4600-GC100000-BASKET0-t10000topographic_no-b_AHP_sngl_10-02-2012neg"
        #dataDir = "{6600.4600.100000.1000}-t1500.recurInh_02.03.13-d"
        dataDir = "data"
        imageName = "./" + dataDir + "/recurInh_i.png"
        fileName = "./" + dataDir + "/spikeTimes"

        f = open(fileName, 'rb') # using 'rb' for windows
        spikeData = cPickle.load(f)
        f.close()

        # Load in locations of the cells
        f = open("./" + dataDir + "/sharedData.pickle", 'rb')  # using 'rb' for windows
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
        GC_xpos = []
        BC_pos = []
        BC_xpos = []

        for ii in spikeData.keys():
            # Medial Entorhinal Area
            if ii < self.num_cells[0]:
                if (ii % 1) == 0:
                    for jj in range(len(spikeData[ii])):
                        if self.t_start <= spikeData[ii][jj] <= self.t_stop:
                            MEA.append(float(ii))
                            MEA_t.append(float(spikeData[ii][jj]))
            # Lateral Entorhinal Area
            elif self.num_cells[0] <= ii < sum(self.num_cells[0:2]):
                if (ii % 1) == 0:
                    for jj in range(len(spikeData[ii])):
                        if self.t_start <= spikeData[ii][jj] <= self.t_stop:
                            LEA.append(ii)
                            LEA_t.append(spikeData[ii][jj])
            # Granule Cell
            elif self.num_cells[0] + self.num_cells[1] <= ii < sum(self.num_cells[0:3]):
                if (ii % 1) == 0:
                    for jj in range(len(spikeData[ii])):
                        if self.t_start <= spikeData[ii][jj] <= self.t_stop:
                            GC.append(ii)
                            GC_t.append(spikeData[ii][jj])
                            GC_pos.append(places[ii][1])
                            GC_xpos.append(places[ii][0])

            # Basket Cell
            elif ii >= sum(self.num_cells[0:3]):
                if (ii % 1) == 0:
                    for jj in range(len(spikeData[ii])):
                        if self.t_start <= spikeData[ii][jj] <= self.t_stop:
                            BC.append(ii)
                            BC_t.append(spikeData[ii][jj])
                            BC_pos.append(BCLocs[ii][1])
                            BC_xpos.append(BCLocs[ii][0])

        self.mea_data = np.array([MEA_t, MEA], dtype=np.float32).transpose()
        self.lea_data = np.array([LEA_t, LEA], dtype=np.float32).transpose()
        self.gc_data = np.array([GC_t, GC_pos], dtype=np.float32).transpose()
        self.bc_data = np.array([BC_t, BC_pos], dtype=np.float32).transpose()

        self.save()


class CellTypeDataSet():
    """
    Set's The data type set into this object

    dataSet : tuple (dataInformation,) # Must be in the format of numpy array
    rgb     : Red, Green, Blue color values ranging from 0 - 1 for these points
    rgbh    : Same values as the 'rgb', this is the highlight color
    xyz     : X, Y, Z Cartesian Coordinates for translating the points
    """

    def __init__(self, title, data_set, rgb=(1, 1, 1), xyz=(0, 0, 0)):
        # create a Vertex Buffer Object with the specified data
        self.vbo = glvbo.VBO(data_set)
        self.count = data_set.shape[0]
        self.rgb = rgb
        self.xyz = xyz
        self.data_set = data_set
        self.title = title

    def setTranslation(self, x, y, z):
        self.xyz = (x, y, z)

    def getTitle(self):
        return self.title

    def setColor(self, r, g, b):
        self.rgb = (r, g, b)

    def getDataSet(self):
        return self.data_set

    def getTranslation(self):
        return gl.glTranslate(self.xyz[0], self.xyz[1], self.xyz[2])

    def getColor(self):
        return gl.glColor(self.rgb[0], self.rgb[1], self.rgb[2])

    def getHighlightColor(self):
        return gl.glColor(self.rgb[0] + .2, self.rgb[1] + .2, self.rgb[2] + .2)

    def getVBO(self):
        return self.vbo