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


class ToolQB():
    """
    SINGLETON
    """
    _instance = None

    def zoom_in(self, QMouseEvent):
        if self.prev_position is None:
            self.prev_position = QMouseEvent.pos()
        else:
            current_position = QMouseEvent.pos()
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

    def mouseDown(self, QMouseEvent):
        self.options[self.tool](self, QMouseEvent)

    def mouseUp(self, QMouseEvent):
        return self.options[self.tool](self, QMouseEvent)

    def __init__(self):
        self.tool = Tools.ZOOM_IN
        self.prev_position = None

    def __new__(cls, *args, **kwargs):
        if not cls._instance:
            cls._instance = super(ToolQB, cls).__new__(
                cls, *args, **kwargs)
        return cls._instance


class CellTypeDataSet():
    """
    Set's The data type set into this object

    dataSet : tuple (dataInformation,) # Must be in the format of numpy array
    rgb     : Red, Green, Blue color values ranging from 0 - 1 for these points
    xyz     : X, Y, Z Cartesian Coordinates for translating the points
    """

    def __init__(self, dataSet, rgb=(1, 1, 1), xyz=(0, 0, 0)):
        # create a Vertex Buffer Object with the specified data
        self.vbo = glvbo.VBO(dataSet)
        self.count = dataSet.shape[0]
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

    def __init__(self, dataSets, view=(0, 1, 0, 1)):
        super(GLPlotWidget, self).__init__()

        self.dataSets = dataSets
        self.setView(view)
        self.toolQB = ToolQB()

    def setView(self, view, projectMouse=False):
        if projectMouse:
            _xLeft, _yBot, z = glu.gluUnProject(view[0], self.height - view[3], 0.0)
            _xRight, _yTop, z = glu.gluUnProject(view[1], self.height - view[2], 0.0)

            self.xLeft = max(self.xLeft, _xLeft)
            self.xRight = min(self.xRight, _xRight)
            self.yBot = max(self.yBot, _yBot)
            self.yTop = min(self.yTop, _yTop)
        else:
            self.xLeft = view[0]
            self.xRight = view[1]
            self.yBot = view[2]
            self.yTop = view[3]

        print (self.xLeft, self.xRight, self.yBot, self.yTop)

        self.setOrtho()

    def setOrtho(self):
        # paint within the whole window
        gl.glViewport(0, 0, self.width, self.height)
        # set orthographic projection (2D only)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glOrtho(self.xLeft, self.xRight, self.yBot, self.yTop, -1, 1)

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

        for dSet in self.dataSets:
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

    def mousePressEvent(self, QMouseEvent):
        self.toolQB.mouseDown(QMouseEvent)

    def mouseReleaseEvent(self, QMouseEvent):
        callback = self.toolQB.mouseUp(QMouseEvent)
        if callback[0] == Callbacks.RESIZE:
            self.setView(callback[1], True)
            self.repaint()

