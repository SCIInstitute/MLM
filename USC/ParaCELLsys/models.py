import OpenGL.GL as gl
import OpenGL.arrays.vbo as glvbo
import os
import cPickle
import numpy as np
from PIL import Image
import math

__author__ = 'mavinm'


def dist_squared(val1, val2):
    return (val1 - val2) ** 2


def getFilteredDataSet(data_set, view):
    data = data_set[
        (view[0] <= data_set[:, 0]) & (data_set[:, 0] <= view[1]) &
        (view[2] <= data_set[:, 1]) & (data_set[:, 1] <= view[3])]
    return data


def rescale_data_to_image(data):
    """
    Normalizes the numpy data matrix to 0-255
    @param data:
    @return:
    """
    return (255.0 / data.max() * (data - data.min())).astype(np.uint8)


class GridGaussian():

    def __init__(self, array, axis, split, sigma):
        if split[0] < 2 or split[1] < 2:
            raise ValueError("Split needs to be at least 2x2")

        self.axis = axis
        self.split = split
        self.dx = float((axis[1] - axis[0])) / float(split[0] - 1)
        self.dy = float((axis[3] - axis[2])) / float(split[1] - 1)

        self.pixels = np.zeros(split)

        self.gaussian_evaluate_pixels(array, sigma)

    def save_image(self):
        rescaled = (255.0 / self.pixels.max() * (self.pixels - self.pixels.min())).astype(np.uint8)
        im = Image.fromarray(rescaled)
        im.show()

    def gaussian_evaluate_pixels(self, array, sigma):
        gaussian_bottom = (2 * math.pi * sigma ** 2)
        for pt in array:
            for i in range(0, self.split[0]):
                for j in range(0, self.split[1]):
                    val_x, val_y = self.map_index(j, i)
                    gaussian_top = math.exp(
                        -(dist_squared(pt[0], val_x) + dist_squared(pt[1], val_y)) / (2 * sigma ** 2))
                    self.pixels[i][j] += gaussian_top / gaussian_bottom

    def map_index(self, x, y):
        val_x = x * self.dx + self.axis[0]
        val_y = y * self.dy + self.axis[2]
        return val_x, val_y


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
        self.bc_data_pos = None
        self.gc_data_pos = None
        self.cell_hierarchy = {}
        self.prev_cell = -1

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
        print "Loading Data is completed"
        pass

    def load_data(self):
        raise NotImplemented("This needs to be implemented and you should call self.save() afterwards for caching")

    def save(self):
        print "ParaCellData.save"
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

        # Saves position coordinates
        np.save(f, self.bc_data_pos)
        np.save(f, self.gc_data_pos)

        f.close()

    def file_on_disk(self):
        if not os.path.isfile(self.rendered_file):
            return self.load_data()

        f = file(self.rendered_file, "rb")

        self.mea_data = np.load(f)
        self.lea_data = np.load(f)
        self.gc_data = np.load(f)
        self.bc_data = np.load(f)

        self.bc_data_pos = np.load(f)
        self.gc_data_pos = np.load(f)

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

    def get_bc_position(self):
        return self.bc_data_pos

    def get_gc_position(self):
        return self.gc_data_pos


class ParseParallelCellData(ParseCellData):
    rendered_file = "tmp/parallelData.bin"

    def __init__(self, num_cells, t_start, t_stop, use_cache_data=False):
        self.mea_data_timelookup = {}
        self.lea_data_timelookup = {}
        self.gc_data_timelookup = {}
        self.bc_data_timelookup = {}
        ParseCellData.__init__(self, num_cells, t_start, t_stop, use_cache_data)

    def load_data(self):
        print "ParseParallelCellData.load_data"
        #dataDir = "MEA6600-LEA4600-GC100000-BASKET0-t10000topographic_no-b_AHP_sngl_10-02-2012neg"
        #dataDir = "{6600.4600.100000.1000}-t1500.recurInh_02.03.13-d"
        dataDir = os.path.dirname(os.path.realpath(__file__)) + "/data"
        print dataDir
        imageName = dataDir + "/recurInh_i.png"
        fileName = dataDir + "/spikeTimes"
        print fileName

        f = open(fileName, 'rb')  # using 'rb' for windows
        spikeData = cPickle.load(f)
        f.close()

        # Load in locations of the cells
        f = open(dataDir + "/sharedData.pickle", 'rb')  # using 'rb' for windows
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

                            # self.add_spiketime_to_cell_hierarchy(ii, float(ii), float(spikeData[ii][jj]))
            # Lateral Entorhinal Area
            elif self.num_cells[0] <= ii < sum(self.num_cells[0:2]):
                if (ii % 1) == 0:
                    for jj in range(len(spikeData[ii])):
                        if self.t_start <= spikeData[ii][jj] <= self.t_stop:
                            LEA.append(ii)
                            LEA_t.append(spikeData[ii][jj])

                            # self.add_spiketime_to_cell_hierarchy(ii, float(ii), float(spikeData[ii][jj]))
            # Granule Cell
            elif self.num_cells[0] + self.num_cells[1] <= ii < sum(self.num_cells[0:3]):
                if (ii % 1) == 0:
                    for jj in range(len(spikeData[ii])):
                        if self.t_start <= spikeData[ii][jj] <= self.t_stop:
                            GC.append(ii)
                            GC_t.append(spikeData[ii][jj])
                            positionThreshold = 6
                            if not self.gc_data_timelookup.has_key(round(places[ii][1], positionThreshold)):
                                self.gc_data_timelookup[round(places[ii][1], positionThreshold)] = []
                            self.gc_data_timelookup[round(places[ii][1], positionThreshold)].append(spikeData[ii][jj])

                            GC_pos.append(places[ii][1])
                            GC_xpos.append(places[ii][0])
                            # self.add_spiketime_to_cell_hierarchy(ii, float(spikeData[ii][jj]), float(places[ii][1]))

            # Basket Cell
            elif ii >= sum(self.num_cells[0:3]):
                if (ii % 1) == 0:
                    for jj in range(len(spikeData[ii])):
                        if self.t_start <= spikeData[ii][jj] <= self.t_stop:
                            BC.append(ii)
                            BC_t.append(spikeData[ii][jj])
                            BC_pos.append(BCLocs[ii][1])
                            BC_xpos.append(BCLocs[ii][0])

                            positionThreshold = 6

                            if not self.bc_data_timelookup.has_key(round(BCLocs[ii][1], positionThreshold)):
                                self.bc_data_timelookup[round(BCLocs[ii][1], positionThreshold)] = []
                            self.bc_data_timelookup[round(BCLocs[ii][1], positionThreshold)].append(spikeData[ii][jj])

                            self.add_spiketime_to_cell_hierarchy(ii, float(spikeData[ii][jj]), float(BCLocs[ii][1]))


        # Storing redundancy for convention with other data that might only have position in the 2nd data slot
        self.mea_data = np.array([MEA_t, MEA], dtype=np.float32).transpose()
        self.lea_data = np.array([LEA_t, LEA], dtype=np.float32).transpose()
        self.gc_data = np.array([GC_t, GC_pos], dtype=np.float32).transpose()
        self.bc_data = np.array([BC_t, BC_pos], dtype=np.float32).transpose()

        # Stores the position into a matrix
        self.bc_data_pos = np.array([BC_xpos, BC_pos], dtype=np.float32).transpose()
        self.gc_data_pos = np.array([GC_xpos, GC_pos], dtype=np.float32).transpose()

        self.save()

    def add_spiketime_to_cell_hierarchy(self, cell_num, x_data, y_data):
        # Creates a spot in the hierarchy if it doesn't exist for this code
        if self.prev_cell != cell_num:
            self.cell_hierarchy[cell_num] = []
            self.prev_cell = cell_num

        self.cell_hierarchy[cell_num].append([x_data, y_data])

    def get_time_point_lookup_data(self):
        return self.mea_data_timelookup, self.lea_data_timelookup, self.gc_data_timelookup, self.bc_data_timelookup



class CellTypeDataSet():
    """
    Sets The data type set into this object

    title   : expecting tuple
    dataSet : tuple (dataInformation,) # Must be in the format of numpy array
    rgb     : Red, Green, Blue color values ranging from 0 - 1 for these points
    rgbh    : Same values as the 'rgb', this is the highlight color
    xyz     : X, Y, Z Cartesian Coordinates for translating the points
    """

    def __init__(self, title, data_set, point_time_lookup, rgb=(1, 1, 1), xyz=(0, 0, 0)):
        # create a Vertex Buffer Object with the specified data
        self.vbo = glvbo.VBO(data_set[:, 0:2])
        self.count = data_set.shape[0]
        self.rgb = rgb
        self.xyz = xyz
        self.data_set = data_set
        self.title = title
        self.point_time_lookup = point_time_lookup

    def setTranslation(self, x, y, z):
        self.xyz = (x, y, z)

    def getAllTimesForPosition(self, x):
        if self.point_time_lookup.has_key(x):
            return self.point_time_lookup[x]
        else:
            return []

    def getTitle(self):
        return self.title

    def setColor(self, r, g, b):
        self.rgb = (r, g, b)

    def getDataSet(self):
        return self.data_set

    def setDataSet(self, data):
        self.data_set = data

    def getFilteredDataSet(self, view):
        data = self.data_set[
            (view[0] <= self.data_set[:, 0]) & (self.data_set[:, 0] <= view[1]) &
            (view[2] <= self.data_set[:, 1]) & (self.data_set[:, 1] <= view[3])]
        return data

    def getTranslation(self):
        return gl.glTranslate(self.xyz[0], self.xyz[1], self.xyz[2])

    def getColor(self, alpha):
        # Set the alpha at .2
        return gl.glColor4f(self.rgb[0], self.rgb[1], self.rgb[2], alpha)

    def getHighlightColor(self):
        return gl.glColor(self.rgb[0] + .2, self.rgb[1] + .2, self.rgb[2] + .2)

    def getVBO(self):
        return self.vbo
