from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QPainter
from PyQt4.QtOpenGL import QGLWidget
from tools import ToolQB, Callbacks
import OpenGL.GL as gl
import OpenGL.GLU as glu
import OpenGL.arrays.vbo as glvbo
import os
import cPickle
import numpy as np

__author__ = 'mavinm'


class ParseCellData():
    """
    use_cache_data : If set to true, ignores parsing the file, instead looks on disk for a cached file binary array

    Returns (MEA_data, LEA_data, GC_data, BC_data)
    """
    rendered_file = "parallelData.bin"

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

        f = file(self.rendered_file, "wb")
        np.save(f, self.mea_data)
        np.save(f, self.lea_data)
        np.save(f, self.gc_data)
        np.save(f, self.bc_data)
        f.close()

    def get_data(self):
        return self.mea_data, self.lea_data, self.gc_data, self.bc_data


class CellTypeDataSet():
    """
    Set's The data type set into this object

    dataSet : tuple (dataInformation,) # Must be in the format of numpy array
    rgb     : Red, Green, Blue color values ranging from 0 - 1 for these points
    xyz     : X, Y, Z Cartesian Coordinates for translating the points
    """

    def __init__(self, data_set, rgb=(1, 1, 1), xyz=(0, 0, 0)):
        # create a Vertex Buffer Object with the specified data
        self.vbo = glvbo.VBO(data_set)
        self.count = data_set.shape[0]
        self.rgb = rgb
        self.xyz = xyz

    def setTranslation(self, x, y, z):
        self.xyz = (x, y, z)

    def setColor(self, r, g, b):
        self.rgb = (r, g, b)

    def getTranslation(self):
        return gl.glTranslate(self.xyz[0], self.xyz[1], self.xyz[2])

    def getColor(self):
        return gl.glColor(self.rgb[0], self.rgb[1], self.rgb[2])

    def getVBO(self):
        return self.vbo


class GLPlotWidget(QGLWidget):
    # default window size
    width, height = 600, 600

    def __init__(self, data_sets, view=(0, 1, 0, 1)):
        QGLWidget.__init__(self)

        self.x_left = 0
        self.x_right = 0
        self.y_bot = 0
        self.y_top = 0
        self.width = 0
        self.height = 0
        self.mouse_origin = 0

        self.data_sets = data_sets
        self.setView(view)
        self.tool_qb = ToolQB()
        print "Address: " + str(id(self.tool_qb))
        self.rubberband = QtGui.QRubberBand(
            QtGui.QRubberBand.Rectangle, self)
        self.setMouseTracking(True)

    def setView(self, view, project_mouse=False):
        if project_mouse:
            _xLeft, _yBot, z = glu.gluUnProject(view[0], self.height - view[3], 0.0)
            _xRight, _yTop, z = glu.gluUnProject(view[1], self.height - view[2], 0.0)

            self.x_left = max(self.x_left, _xLeft)
            self.x_right = min(self.x_right, _xRight)
            self.y_bot = max(self.y_bot, _yBot)
            self.y_top = min(self.y_top, _yTop)
        else:
            self.x_left = view[0]
            self.x_right = view[1]
            self.y_bot = view[2]
            self.y_top = view[3]

        print "(xl,xr,yb,yt) = ", (self.x_left, self.x_right, self.y_bot, self.y_top)

        self.setOrtho()

    def setOrtho(self):
        # paint within the whole window
        gl.glViewport(0, 0, self.width, self.height)
        # set orthographic projection (2D only)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glOrtho(self.x_left, self.x_right, self.y_bot, self.y_top, -1, 1)

    def initializeGL(self):
        """Initialize OpenGL, VBOs, upload data on the GPU, etc.
        """
        # background color
        gl.glClearColor(1, 1, 1, 1)

    def paintGL(self):
        """Paint the scene.
        """
        # clear the buffer
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        print "Painting"

        for dSet in self.data_sets:
            # set blue color for subsequent drawing rendering calls
            dSet.getColor()
            gl.glPushMatrix()
            dSet.getTranslation()
            # bind the VBO
            dSet.getVBO().bind()
            # tell OpenGL that the VBO contains an array of vertices
            gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
            # these vertices contain 2 single precision coordinates
            gl.glVertexPointer(2, gl.GL_FLOAT, 0, dSet.getVBO())
            # draw "count" points from the VBO
            gl.glDrawArrays(gl.GL_POINTS, 0, dSet.count)
            gl.glPopMatrix()

        gl.glFlush()

    def resizeGL(self, width, height):
        """Called upon window resizing: reinitialize the viewport.
        """
        # update the window size
        self.width, self.height = width, height
        self.setOrtho()

    def mousePressEvent(self, event):
        print "Mouse Down Event"
        self.mouse_origin = event.pos()
        self.rubberband.setGeometry(
            QtCore.QRect(self.mouse_origin, QtCore.QSize()))
        self.rubberband.show()

        self.tool_qb.mouse_down(event)
        QtGui.QWidget.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        if self.rubberband.isVisible():
            self.rubberband.setGeometry(
                QtCore.QRect(self.mouse_origin, event.pos()).normalized())
            QtGui.QWidget.mouseMoveEvent(self, event)

    def mouseReleaseEvent(self, event):
        print "Mouse Up Event"
        if self.rubberband.isVisible():
            self.rubberband.hide()
        callback = self.tool_qb.mouse_up(event)
        if callback[0] == Callbacks.RESIZE:
            self.setView(callback[1], True)
            self.repaint()

        QtGui.QWidget.mouseReleaseEvent(self, event)

