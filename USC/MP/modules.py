from PyQt4 import QtGui, QtCore
from PyQt4.QtGui import QPainter
from PyQt4.QtOpenGL import QGLWidget
import OpenGL.GL as gl
import OpenGL.GLU as glu
import OpenGL.arrays.vbo as glvbo
from enum import Enum
import math

__author__ = 'mavinm'


class Tools(Enum):
    NONE = 0
    ZOOM_IN = 1


class Callbacks(Enum):
    NONE = 0
    RESIZE = 1


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class ToolQB():

    __metaclass__ = Singleton

    def zoom_in(self, mouse):
        if self.prev_position is None:
            self.prev_position = mouse.pos()
        else:
            current_position = mouse.pos()
            prev_xy = (self.prev_position.x(), self.prev_position.y())
            curr_xy = (current_position.x(), current_position.y())
            dist = math.hypot(curr_xy[0] - prev_xy[0],
                              curr_xy[1] - prev_xy[1])
            if dist < 2:
                print "Treat as a click"
                callback = Callbacks.NONE
            else:
                print "Zoom in"
                callback = Callbacks.RESIZE
            self.prev_position = None

            return callback, (
                min(curr_xy[0], prev_xy[0]), max(curr_xy[0], prev_xy[0]),
                min(curr_xy[1], prev_xy[1]), max(curr_xy[1], prev_xy[1]))

    options = {
        Tools.ZOOM_IN: zoom_in,
    }

    def mouse_down(self, mouse):
        self.options[self.tool](self, mouse)

    def mouse_up(self, mouse):
        return self.options[self.tool](self, mouse)

    def __init__(self):
        self.tool = Tools.ZOOM_IN
        self.prev_position = None


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
        print "Address 1: " + str(id(self.tool_qb))
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

