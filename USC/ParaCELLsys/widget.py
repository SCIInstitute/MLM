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
import threading
import time

__author__ = 'Mavin Martin'


class GuiCellPlot(QtGui.QMainWindow):
    """
    Singleton: plots all of the cells in one graph and is called in main.
    """

    def __init__(self, mea_lea_tile, gc_tile, bc_tile):
        super(GuiCellPlot, self).__init__()
        self.central = QWidget(self)

        # these are the default height of the window
        self.width = 800
        self.height = 600

        # all three plots as widgets with separate labels.
        # We want these as separate blocks so we can have axis and things
        mea_lea_label = QtGui.QLabel(mea_lea_tile.get_Title(), self)
        mea_lea_label.setAutoFillBackground(True)
        mea_lea_widget = GLUIWidget(mea_lea_tile)
        gc_label = QtGui.QLabel(gc_tile.get_Title(), self)
        gc_label.setAutoFillBackground(True)
        gc_widget = GLUIWidget(gc_tile)
        bc_label = QtGui.QLabel(bc_tile.get_Title(), self)
        bc_label.setAutoFillBackground(True)
        bc_widget = GLUIWidget(bc_tile)

        self.widgets = (mea_lea_widget, gc_widget, bc_widget)

        #self.grid = QtGui.QGridLayout(self.central)
        #self.grid.setSpacing(0)
        #self.grid.setRowMinimumHeight(0, 1)

        self.boxy = QtGui.QVBoxLayout(self.central)

        # add all the plot widgets and labels to the layout
        self.boxy.addWidget(bc_label, 0, QtCore.Qt.AlignRight)      #, 0, 0)
        self.boxy.addWidget(bc_widget, 2)                           #, 1, 0)
        self.boxy.addWidget(gc_label, 0, QtCore.Qt.AlignRight)      #, 2, 0)
        self.boxy.addWidget(gc_widget, 8)                           #, 3, 0, 6, 0)  # row x, col y, w row, h col
        self.boxy.addWidget(mea_lea_label, 0, QtCore.Qt.AlignRight) #, 8, 0)
        self.boxy.addWidget(mea_lea_widget, 3)                      #, 9, 0, 2, 0)

        self.resize(self.width, self.height)
        self.setWindowTitle("ParaCELLsys")

        self.setCentralWidget(self.central)

    def keyPressEvent(self, QKeyEvent):
        # 67 = 'c'
        if QKeyEvent.key() == 67:
            print 'c pressed'
        # 68 = 'd'
        elif QKeyEvent.key() == 68:
            for child in self.boxy.children():
                print child

        print QKeyEvent.key()

    def closeEvent(self, QCloseEvent):
        for widget in self.widgets:
            widget.closeEvent(QCloseEvent)


class GLPlotWidget(QGLWidget, threading.Thread):
    """
    Anything here is just for the plot objects
    """

    def __init__(self, viewer):
        QGLWidget.__init__(self)
        threading.Thread.__init__(self)

        self.program_active = True
        self.mouse_origin = 0
        self.alpha = .2
        self.mouse_pos = None

        self.view = viewer.get_View()
        self.data_sets = viewer.get_Data()
        self.title = viewer.get_Title()
        self.tool_qb = ToolQB()
        self.rubberband = RectRubberband()
        self.setMouseTracking(True)
        self.prevView = None

        self.kd_tree = []
        self.kd_tree_active = False
        self.graphicsProxyWidget()
        self.scale_x = 0
        self.scale_y = 0
        self.width = 0
        self.height = 0

        # draw axes

        # Starts the thread of anything inside of the run() method
        self.start()

    def recreate_kd_tree(self):
        # highlighting using the kd_tree method being iterated over time
        for dset in self.data_sets:
            self.scale_x = self.view.width()
            self.scale_y = self.view.height()

            _data = np.array(dset.getFilteredDataSet(self.view.view()), copy=True)
            _data[:, 0] /= float(self.scale_x)
            _data[:, 1] /= float(self.scale_y)
            self.kd_tree.append(
                KDTreeWritable(dset.getTitle(), _data, leafsize=100,
                               use_cache_data=False).load()
            )
        print "kd_tree complete for " + self.title
        self.kd_tree_active = True

    def run(self):
        # TODO - HANDLE Program exiting
        while self.program_active:

            if not self.kd_tree_active:
                self.kd_tree = []
                print "Creating kd_tree for " + self.title
                self.recreate_kd_tree()

            time.sleep(.25)

    def setAlpha(self):
        print "Setting alpha"

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

    # flesh this out- want to have it dynamically resize
    def draw_axes(self, axis1, axis2):
        pass

    def initializeGL(self):
        """
        Initialize OpenGL, VBOs, upload data on the GPU, etc.
        """
        # background color
        gl.glClearColor(1, 1, 1, 1)

    def mouseMoveEvent(self, event):
        self.mouse_pos = event.pos()
        QGLWidget.mouseMoveEvent(self, event)

    def find_data_pos(self):
        """
        Looks at mouse position and calculates data position of data point closest to cursor
        Returns: (tree number, point number, distance from cursor, x-position in view, y-position in view
        """
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
        if not self.kd_tree_active:
            return

        gl.glEnable(gl.GL_POINT_SMOOTH)

        tree_num, pt_num, distance, x, y = self.find_data_pos()

        self.data_sets[tree_num].getHighlightColor()
        gl.glPushMatrix()
        gl.glPointSize(10)
        gl.glBegin(gl.GL_POINTS)
        gl.glVertex2f(x, y)
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
        gl.glEnable(gl.GL_BLEND)
        gl.glBlendFunc(gl.GL_SRC_ALPHA, gl.GL_ONE_MINUS_SRC_ALPHA)


        #gl.glUseProgram(self.highlight_shader)
        #if self.mouse_pos is not None:
        #    x_, y_, z_ = glu.gluUnProject(self.mouse_pos.x(), self.height - self.mouse_pos.y(), 0)
        #    gl.glUniform2f(self.mouse_pos_handler, x_, y_)
        #    gl.glUniform2f(self.window_size_handler, self.view.width(), self.view.height())

        # dSet = CellTypeDataSet()
        for dSet in self.data_sets:
            # set blue color for subsequent drawing rendering calls
            dSet.getColor(self.alpha)
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
        """
        Called upon window resizing: reinitialize the viewport.
        """
        # update the window size
        self.width, self.height = width, height
        self.setOrtho(self.view.view())

        QGLWidget.resizeGL(self, width, height)

    def resetToOriginalView(self):
        print "Resetting to original view: " + str(self.view.orig_view)
        self.setOrtho(self.view.orig_view)
        self.view.set_view(self.view.orig_view)
        self.kd_tree_active = False

    def closeEvent(self, QCloseEvent):
        print "Closing event called"
        self.program_active = False

        QGLWidget.closeEvent(self, QCloseEvent)


def convertMousePoint2DrawPlane(event_pos, height):
    return QtCore.QPoint(event_pos.x(), height - event_pos.y())


class GLUIWidget(UI, GLPlotWidget):
    """
    Widget class for the three cell plots. Called in GuiCellPlot. Inherits from GLPlotWidget
    """

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
        self.tool_qb.mouse_down(event, Tools.SCALING, window_height=self.height)

    def mouseReleaseEventLeft(self, event):
        self.rubberband.hide()
        callback = self.tool_qb.mouse_up(event, Tools.ZOOM_IN, parent=self)
        if callback == Callbacks.RESIZE:
            print "Resizing"
            if self.rubberband.box.dataDistance() > .1:
                self.view.set_view(self.rubberband.box.unprojectView())
                self.setOrtho(self.view.view())
            else:
                QMessageBox.about(self, "ERROR", "Your view window is too small to compute.")
            self.kd_tree_active = False
            self.repaint()
        elif callback == Callbacks.CLICK:
            if not self.kd_tree_active:
                print "Data is still being evaluated, please wait"
                return
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
            """
            if self.view.orig_view[0] > self.prevView[0]:
                self.prevView[0] = self.view.orig_view[0]
            if self.view.orig_view[1] > self.prevView[1]:
                self.prevView[1] = self.view.orig_view[1]
            if self.view.orig_view[2] > self.prevView[2]:
                self.prevView[2] = self.view.orig_view[2]
            if self.view.orig_view[3] > self.prevView[3]:
                self.prevView[3] = self.view.orig_view[3]
                """
            self.view.set_view(self.prevView)
            self.repaint()
            if callback == Callbacks.CLICK:
                tree_num, pt_num, distance, x, y = self.find_data_pos()
                print "Focus Point Number= " + str(pt_num)
                print "Distance from Mouse= " + str(distance)
                print "Point = (" + str(x) + ", " + str(y) + ")"

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

