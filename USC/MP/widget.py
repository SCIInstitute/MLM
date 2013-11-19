from globals import *
from kdtree import KDTreeWritable
from PyQt4 import QtGui
from PyQt4.QtGui import QWidget, QMessageBox
from PyQt4 import QtCore
from PyQt4.QtOpenGL import QGLWidget
from rubberband import RectRubberband
from shaders import ShaderCreator
from tools import ToolQB, Callbacks, Tools
import OpenGL.GL as gl
import OpenGL.GLU as glu
import numpy as np
from ui import UI

__author__ = 'Mavin Martin'


class GuiCellPlot(QtGui.QMainWindow):
    """
    Plots all of the cells in one graph
    """

    width = 800
    height = 500

    def __init__(self, mea_lea_tile, gc_tile, bc_tile):
        super(GuiCellPlot, self).__init__()
        self.central = QWidget(self)

        mea_lea_widget = GLUIWidget(mea_lea_tile)
        gc_widget = GLUIWidget(gc_tile)
        bc_widget = GLUIWidget(bc_tile)

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

    def __init__(self, viewer):
        QGLWidget.__init__(self)

        self.width = 0
        self.height = 0
        self.mouse_origin = 0
        self.quadric = None
        self.highlight_shader = None
        self.mouse_pos = None

        self.view = viewer.get_View()

        self.data_sets = viewer.get_Data()
        self.tool_qb = ToolQB()
        self.rubberband = RectRubberband()
        self.setMouseTracking(True)

        self.kd_tree = []

        self.graphicsProxyWidget()

        for dset in self.data_sets:
            self.scale_x = viewer.view.width()
            self.scale_y = viewer.view.height()
            _data = np.array(dset.getDataSet(), copy=True)
            _data = _data.transpose()
            _data[0] /= float(self.scale_x)
            _data[1] /= float(self.scale_y)
            _data = _data.transpose()
            self.kd_tree.append(
                KDTreeWritable(dset.getTitle(), _data, leafsize=100, use_cache_data=USE_CACHING).load()
            )

    def event(self, QEvent):
        if QEvent.type() == QtCore.QEvent.Leave:
            self.mouse_pos = None
            self.repaint()

        return QGLWidget.event(self, QEvent)

    def setOrtho(self, viewArray):
        # paint within the whole window
        gl.glViewport(0, 0, self.width, self.height)
        # set orthographic projection (2D only)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()
        if (viewArray[0] == viewArray[1]) or (viewArray[2] == viewArray[3]):
            QMessageBox.about(self, "ERROR", "Your view window is too small to compute.")
            viewArray = self.prevView
        else:
            self.prevView = [viewArray[0], viewArray[1], viewArray[2], viewArray[3]]
        gl.glOrtho(viewArray[0], viewArray[1], viewArray[2], viewArray[3], -100, 100)
        self.repaint()

    def scaleOrtho(self, delta):
        mouse_pos = self.tool_qb.get_scale_anchor()
        scale = 1 - delta
        # Normalizes the vector, scales it, then puts it back into world coordinates
        l = (self.view.left - mouse_pos[0]) * scale + mouse_pos[0]
        r = (self.view.right - mouse_pos[0]) * scale + mouse_pos[0]
        t = (self.view.top - mouse_pos[1]) * scale + mouse_pos[1]
        b = (self.view.bottom - mouse_pos[1]) * scale + mouse_pos[1]

        self.setOrtho((l, r, b, t))

    def initializeGL(self):
        """
        Initialize OpenGL, VBOs, upload data on the GPU, etc.
        """
        # background color
        gl.glClearColor(1, 1, 1, 1)
        self.highlight_shader = self.createShader("shaders/mouseHover.vs", "shaders/mouseHover.fs")
        self.mouse_pos_handler = gl.glGetUniformLocation(self.highlight_shader, "mouse_pos")
        self.window_size_handler = gl.glGetUniformLocation(self.highlight_shader, "window_size")
        self.quadric = glu.gluNewQuadric()
        glu.gluQuadricNormals(self.quadric, glu.GLU_SMOOTH)

    def mouseMoveEvent(self, event):
        self.mouse_pos = event.pos()
        QGLWidget.mouseMoveEvent(self, event)

    """
    Looks at mouse position and cacluates data position of data point closest to cursor

    Returns: (tree number, point number, distance from cursor, x-position in view, y-position in view
    """

    def find_data_pos(self):
        x_, y_, z_ = glu.gluUnProject(self.mouse_pos.x(), self.height - self.mouse_pos.y(), 0)

        x_ /= self.scale_x
        y_ /= self.scale_y

        d = 99999999999
        pt_num = -1
        tree_num = -1
        for i in range(0, len(self.kd_tree)):
            _d, _pt_num = self.kd_tree[i].query([x_, y_])
            if _d < d:
                tree_num = i
                pt_num = _pt_num
                d = _d
        if pt_num == -1 or tree_num == -1:
            raise KeyError("Unable to get information")
        focus_x, focus_y = self.kd_tree[tree_num].data[pt_num]
        return tree_num, pt_num, d, focus_x * self.scale_x, focus_y * self.scale_y

    def draw_kd_tree_point(self):
        gl.glEnable(gl.GL_POINT_SMOOTH)

        tree_num, pt_num, distance, x, y = self.find_data_pos()

        self.data_sets[tree_num].getHighlightColor()
        gl.glPushMatrix()
        gl.glTranslatef(x, y, 0)
        gl.glPointSize(10)
        gl.glBegin(gl.GL_POINTS)
        gl.glVertex2f(0, 0)
        gl.glEnd()
        gl.glPointSize(1)
        gl.glPopMatrix()
        gl.glDisable(gl.GL_POINT_SMOOTH)

    def paintGL(self):
        """
        Paint the scene.
        """
        # clear the buffer
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        #gl.glUseProgram(self.highlight_shader)
        #if self.mouse_pos is not None:
        #    x_, y_, z_ = glu.gluUnProject(self.mouse_pos.x(), self.height - self.mouse_pos.y(), 0)
        #    gl.glUniform2f(self.mouse_pos_handler, x_, y_)
        #    gl.glUniform2f(self.window_size_handler, self.view.width(), self.view.height())

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
            #gl.glUseProgram(0)

        if self.mouse_pos is not None and not self.rubberband.isVisible():
            self.draw_kd_tree_point()

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
        self.view.set_view(self.view.orig_view)

    def closeEvent(self, QCloseEvent):
        glu.gluDeleteQuadric(self.quadratic)

        gl.glDeleteShader(self.highlight_shader)
        glu.gluDeleteQuadric(self.quadric)

        QGLWidget.closeEvent(self, QCloseEvent)


def convertMousePoint2DrawPlane(event_pos, height):
    return QtCore.QPoint(event_pos.x(), height - event_pos.y())


class GLUIWidget(UI, GLPlotWidget):
    def __init__(self, viewer):
        GLPlotWidget.__init__(self, viewer)

    def mousePressEventLeft(self, event):
        print "Mouse Down Event"
        self.mouse_origin = convertMousePoint2DrawPlane(event.pos(), self.height)
        self.rubberband.setGeometry(
            QtCore.QRect(self.mouse_origin, QtCore.QSize()))
        self.rubberband.show()

        self.tool_qb.mouse_down(event, Tools.ZOOM_IN)

    def mousePressEventRight(self, event):
        self.tool_qb.mouse_down(event, Tools.SCALING, self.height)

    def mouseReleaseEventLeft(self, event):
        self.rubberband.hide()
        callback = self.tool_qb.mouse_up(event, Tools.ZOOM_IN)
        if callback == Callbacks.RESIZE:
            print "Resizing"
            if self.rubberband.box.dataDistance() > .1:
                self.view.set_view(self.rubberband.box.unprojectView())
                self.setOrtho(self.view.view())
            else:
                QMessageBox.about(self, "ERROR", "Your view window is too small to compute, reloading original view.")
                self.resetToOriginalView()
            self.repaint()
        if callback == Callbacks.CLICK:
            tree_num, pt_num, distance, x, y = self.find_data_pos()
            print "Focus Point Number= " + str(pt_num)
            print "Distance from Mouse= " + str(distance)
            print "Point = (" + str(x) + ", " + str(y) + ")"

    def mouseReleaseEventRight(self, event):
        callback = self.tool_qb.mouse_up(event, Tools.SCALING)
        if callback == Callbacks.CLICK:
            self.resetToOriginalView()
        else:
            # See's if the view window is larger than the data window
            if self.view.orig_view[0] > self.prevView[0]:
                self.prevView[0] = self.view.orig_view[0]
            if self.view.orig_view[1] > self.prevView[1]:
                self.prevView[1] = self.view.orig_view[1]
            if self.view.orig_view[2] > self.prevView[2]:
                self.prevView[2] = self.view.orig_view[2]
            if self.view.orig_view[3] > self.prevView[3]:
                self.prevView[3] = self.view.orig_view[3]
            self.view.set_view(self.prevView)

    def mouseMoveEvent(self, event):
        if self.rubberband.isVisible():
            self.rubberband.setGeometry(
                QtCore.QRect(self.mouse_origin, convertMousePoint2DrawPlane(event.pos(), self.height)).normalized())

        if self.tool_qb.scaling_in_effect():
            distance = self.tool_qb.mouse_move(event, Tools.SCALING)
            delta = distance / float(self.width)
            self.scaleOrtho(delta)

        self.repaint()

        GLPlotWidget.mouseMoveEvent(self, event)

