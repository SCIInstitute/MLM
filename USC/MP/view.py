from PyQt4 import QtGui
from PyQt4.QtGui import QWidget
from PyQt4 import QtCore
from PyQt4.QtOpenGL import QGLWidget
from tools import ToolQB, Callbacks
import OpenGL.GL as gl
import OpenGL.GLU as glu

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


class Viewer():
    def __init__(self, *args, **kwargs):
        num_args = len(args)
        if num_args == 0:
            self.__initializeView((0, 1, 0, 1))
        elif num_args == 1:
            self.__initializeView(args[0])
        elif num_args == 4:
            self.__initializeView((args[0], args[1], args[2], args[3]))
        else:
            raise KeyError("You did not meet the Viewer() initialization criteria")


    def __initializeView(self, view):
        self.set_view(view[0], view[1], view[2], view[3])

        self.orig_view = (view[0], view[1], view[2], view[3])

    def view(self):
        return self.left, self.right, self.bottom, self.top

    def set_view(self, left, right, bottom, top):
        self.left = left
        self.right = right
        self.bottom = bottom
        self.top = top

    def reset_view(self):
        self.left, self.right, self.bottom, self.top = self.orig_view

    def unprojectedView(self):
        _left, _bottom, z = glu.gluUnProject(self.left, self.bottom, 0.0)
        _right, _top, z = glu.gluUnProject(self.right, self.top, 0.0)

        return _left, _right, _bottom, _top


class ViewTile():
    """
    Keeps Track of the data sets along with window information like view size, etc.

    data_set : CellTypeDataSet(dataSet, rgb, xyz) # Cell Data being read in
    view     : (x_left, x_right, y_bottom, y_top) # The window sizes to show the data
    """

    def __init__(self, data_set, view):
        self.data_set = data_set
        self.view = Viewer(view)


class CustomRubberband():
    def __init__(self):
        self.visible = False
        self.box = Viewer()

    def draw(self):
        gl.glLineWidth(2.5)
        gl.glColor3f(100, 0, 0)
        gl.glBegin(gl.GL_LINES)
        gl.glVertex2f(self.box.left, self.box.top)
        gl.glVertex2f(self.box.left, self.box.bottom)
        gl.glVertex2f(self.box.left, self.box.bottom)
        gl.glVertex2f(self.box.right, self.box.bottom)
        gl.glVertex2f(self.box.right, self.box.bottom)
        gl.glVertex2f(self.box.right, self.box.top)
        gl.glVertex2f(self.box.right, self.box.top)
        gl.glVertex2f(self.box.left, self.box.top)
        gl.glEnd()

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False

    def isVisible(self):
        return self.visible

    def setGeometry(self, event, height, view):
        self.box.updateView()
        self.left, self.bottom, z = glu.gluUnProject(event.left(), height - event.bottom(), 0.0)
        self.right, self.top, z = glu.gluUnProject(event.right(), height - event.top(), 0.0)

        #if self.left < view[0]:
        #    self.left = view[0]
        #
        #if self.right > view[1]:
        #    self.right = view[1]
        #
        #if self.bottom < view[2]:
        #    self.bottom = view[2]
        #
        #if self.top > view[3]:
        #    self.top = view[3]


class GLPlotWidget(QGLWidget):
    # default window size
    width, height = 600, 600

    def __init__(self, data_sets, view):
        QGLWidget.__init__(self)

        self.width = 0
        self.height = 0
        self.mouse_origin = 0
        self.view = view
        self.orig_view = view

        self.data_sets = data_sets
        self.setView(view)
        self.tool_qb = ToolQB()
        self.rubberband = CustomRubberband()
        self.setMouseTracking(True)

    def setView(self, view, unproject_mouse=False):
        if unproject_mouse:
            _xLeft, _yBot, z = glu.gluUnProject(view[0], self.height - view[3], 0.0)
            _xRight, _yTop, z = glu.gluUnProject(view[1], self.height - view[2], 0.0)

            x_left = max(self.view[0], _xLeft)
            x_right = min(self.view[1], _xRight)
            y_bot = max(self.view[2], _yBot)
            y_top = min(self.view[3], _yTop)

            self.view = (x_left, x_right, y_bot, y_top)

        self.setOrtho()

    def setOrtho(self):
        # paint within the whole window
        gl.glViewport(0, 0, self.width, self.height)
        # set orthographic projection (2D only)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        gl.glOrtho(self.view.left, self.view.right, self.view.bottom, self.view.top, -1, 1)
        self.repaint()

    def initializeGL(self):
        """
        Initialize OpenGL, VBOs, upload data on the GPU, etc.
        """
        # background color
        gl.glClearColor(1, 1, 1, 1)
        # TODO - Place only if the person zoom's in more than 50%
        #gl.glEnable(gl.GL_POINT_SMOOTH)

    def paintGL(self):
        """
        Paint the scene.
        """
        # clear the buffer
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

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

        if self.rubberband.isVisible():
            self.rubberband.draw()

        gl.glFlush()

    def resizeGL(self, width, height):
        """Called upon window resizing: reinitialize the viewport.
        """
        # update the window size
        self.width, self.height = width, height
        self.setOrtho()

    def resetToOriginalView(self):
        print "Resetting to original view: " + str(self.orig_view)
        self.setView(self.orig_view)

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.mousePressEventLeft(event)

        if event.button() == QtCore.Qt.RightButton:
            self.mousePressEventRight(event)

        QGLWidget.mousePressEvent(self, event)

    def mousePressEventRight(self, event):
        pass

    def mousePressEventLeft(self, event):
        pass

    def mouseMoveEvent(self, event):
        if self.rubberband.isVisible():
            self.rubberband.setGeometry(
                QtCore.QRect(self.mouse_origin, event.pos()).normalized(), self.height, self.view)
            self.repaint()

        QGLWidget.mouseMoveEvent(self, event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            print "Mouse Up Event"
            if self.rubberband.isVisible():
                self.rubberband.hide()
                callback = self.tool_qb.mouse_up(event)
                if callback[0] == Callbacks.RESIZE:
                    self.setView(callback[1], True)
                    self.repaint()

        QGLWidget.mouseReleaseEvent(self, event)


class GLUIWidget(GLPlotWidget):
    def __init__(self, data_sets, view=(0, 1, 0, 1)):
        GLPlotWidget.__init__(self, data_sets, view)

    def mousePressEventLeft(self, event):
        print "Mouse Down Event"
        self.mouse_origin = event.pos()
        self.rubberband.setGeometry(
            QtCore.QRect(self.mouse_origin, QtCore.QSize()), self.height, self.view)
        self.rubberband.show()

        self.tool_qb.mouse_down(event)

    def mousePressEventRight(self, event):
        self.resetToOriginalView()