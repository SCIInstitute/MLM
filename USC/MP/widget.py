from PyQt4 import QtGui
from PyQt4.QtGui import QWidget
from PyQt4 import QtCore
from PyQt4.QtOpenGL import QGLWidget
from rubberband import RectRubberband
from shaders import ShaderCreator
from tools import ToolQB, Callbacks
import OpenGL.GL as gl
import OpenGL.GLU as glu
from ui import UI

__author__ = 'mavinm'


class GuiCellPlot(QtGui.QMainWindow):
    """
    Plots all of the cells in one graph
    """

    width = 800
    height = 500

    def __init__(self, mea_lea_tile, gc_tile, bc_tile):
        super(GuiCellPlot, self).__init__()
        self.central = QWidget(self)

        mea_lea_widget = GLUIWidget(mea_lea_tile.data_set, mea_lea_tile.view)
        gc_widget = GLUIWidget(gc_tile.data_set, gc_tile.view)
        bc_widget = GLUIWidget(bc_tile.data_set, bc_tile.view)

        self.grid = QtGui.QGridLayout(self.central)
        self.grid.setSpacing(10)

        self.grid.addWidget(bc_widget, 1, 0)
        self.grid.addWidget(gc_widget, 2, 0, 5, 0)
        self.grid.addWidget(mea_lea_widget, 7, 0, 2, 0)

        self.resize(self.width, self.height)
        self.setWindowTitle("Cell Plot")

        self.setCentralWidget(self.central)


class GLPlotWidget(QGLWidget, ShaderCreator):
    # default window size
    width, height = 600, 600

    def __init__(self, data_sets, view):
        QGLWidget.__init__(self)

        self.width = 0
        self.height = 0
        self.mouse_origin = 0
        self.view = view

        self.data_sets = data_sets
        self.tool_qb = ToolQB()
        self.rubberband = RectRubberband()
        self.setMouseTracking(True)
        self.highlight_shader = None

    def setOrtho(self, viewArray):
        # paint within the whole window
        gl.glViewport(0, 0, self.width, self.height)
        # set orthographic projection (2D only)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glOrtho(viewArray[0], viewArray[1], viewArray[2], viewArray[3], -.1, .1)
        self.repaint()

    def initializeGL(self):
        """
        Initialize OpenGL, VBOs, upload data on the GPU, etc.
        """
        # background color
        gl.glClearColor(1, 1, 1, 1)
        # TODO - Place only if the person zoom's in more than 50%
        #gl.glEnable(gl.GL_POINT_SMOOTH)
        self.highlight_shader = self.createShader("shaders/mouseHover.vs", "shaders/mouseHover.fs")


    def paintGL(self):
        """
        Paint the scene.
        """
        # clear the buffer
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        gl.glUseProgram(self.highlight_shader)
        #gl.gluniform2f()
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
        gl.glUseProgram(0)

        if self.rubberband.isVisible():
            self.rubberband.restrictBoundaries(self.width, self.height)
            self.rubberband.draw()

        gl.glFlush()

    def resizeGL(self, width, height):
        """Called upon window resizing: reinitialize the viewport.
        """
        # update the window size
        self.width, self.height = width, height
        self.setOrtho(self.view.view())

        QGLWidget.resizeGL(self, width, height)

    def resetToOriginalView(self):
        print "Resetting to original view: " + str(self.view.orig_view)
        self.setOrtho(self.view.orig_view)

    def closeEvent(self, QCloseEvent):
        glu.gluDeleteQuadric(self.quadratic)

        gl.glDeleteShader(self.highlight_shader)

        QGLWidget.closeEvent(self, QCloseEvent)


def convertMousePoint2DrawPlane(event_pos, height):
    return QtCore.QPoint(event_pos.x(), height - event_pos.y())


class GLUIWidget(UI, GLPlotWidget):
    def __init__(self, data_sets, view=(0, 1, 0, 1)):
        GLPlotWidget.__init__(self, data_sets, view)

    def mousePressEventLeft(self, event):
        print "Mouse Down Event"
        self.mouse_origin = convertMousePoint2DrawPlane(event.pos(), self.height)
        self.rubberband.setGeometry(
            QtCore.QRect(self.mouse_origin, QtCore.QSize()))
        self.rubberband.show()

        self.tool_qb.mouse_down(event)

    def mousePressEventRight(self, event):
        self.resetToOriginalView()

    def mouseReleaseEventLeft(self, event):
        print "Mouse Up Event"
        if self.rubberband.isVisible():
            self.rubberband.hide()
            callback = self.tool_qb.mouse_up(event)
            if callback[0] == Callbacks.RESIZE:
                self.view.set_view(self.rubberband.box.unprojectView())
                self.setOrtho(self.view.view())
                self.repaint()

    def mouseMoveEvent(self, event):
        if self.rubberband.isVisible():
            self.rubberband.setGeometry(
                QtCore.QRect(self.mouse_origin, convertMousePoint2DrawPlane(event.pos(), self.height)).normalized())

        self.repaint()

        QGLWidget.mouseMoveEvent(self, event)
