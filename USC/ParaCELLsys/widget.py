from kdtree import KDTreeWritable
from PyQt4 import QtGui
from PyQt4.QtGui import QWidget, QMessageBox
from PyQt4 import QtCore
from PyQt4.QtOpenGL import QGLWidget
from rubberband import RectRubberband
from tools import ToolQB, Callbacks, Tools
import OpenGL.GL as gl
import OpenGL.GLU as glu
import OpenGL.arrays.vbo as glvbo
import numpy as np
from ui import UI
import threading
import thread
import time

__author__ = 'Mavin Martin'


class GuiCellPlot(QtGui.QMainWindow, threading.Thread):
    """
    Singleton: plots all of the cells in one graph and is called in main.
    """

    # The default height of the window
    width = 1000
    height = 700

    def __init__(self, mea_lea_tile, gc_tile, bc_tile, cell_hierarchy={}):
        super(GuiCellPlot, self).__init__()
        threading.Thread.__init__(self)
        self.central = QWidget(self)

        # Makes the widget size not resizable
        self.setFixedSize(self.width, self.height)

        # all three plots as widgets with separate labels.
        # We want these as separate blocks so we can have axis and things
        mea_lea_label = QtGui.QLabel(mea_lea_tile.get_Title(), self)
        mea_lea_label.setAutoFillBackground(True)
        mea_lea_widget = FigureDiagramWidget(mea_lea_tile)
        gc_label = QtGui.QLabel(gc_tile.get_Title(), self)
        gc_label.setAutoFillBackground(True)
        gc_widget = FigureDiagramWidget(gc_tile)
        bc_label = QtGui.QLabel(bc_tile.get_Title(), self)
        bc_label.setAutoFillBackground(True)
        bc_widget = FigureDiagramWidget(bc_tile)

        self.widgets = (mea_lea_widget, gc_widget, bc_widget)

        #self.grid = QtGui.QGridLayout(self.central)
        #self.grid.setSpacing(0)
        #self.grid.setRowMinimumHeight(0, 1)

        self.boxy = QtGui.QVBoxLayout(self.central)

        # add all the plot widgets and labels to the layout
        self.boxy.addWidget(bc_label, 0, QtCore.Qt.AlignRight)  # , 0, 0)
        self.boxy.addWidget(bc_widget, 2)  # , 1, 0)
        self.boxy.addWidget(gc_label, 0, QtCore.Qt.AlignRight)  # , 2, 0)
        self.boxy.addWidget(gc_widget, 8)  # , 3, 0, 6, 0)  # row x, col y, w row, h col
        self.boxy.addWidget(mea_lea_label, 0, QtCore.Qt.AlignRight)  # , 8, 0)
        self.boxy.addWidget(mea_lea_widget, 3)  # , 9, 0, 2, 0)

        self.statusBar().showMessage("Ready")

        self.resize(self.width, self.height)
        self.setWindowTitle("ParaCELLsys")

        self.setCentralWidget(self.central)
        self.program_active = True
        self.start()

        self.vbos = []
        for cell_num in cell_hierarchy:
            data = np.array(cell_hierarchy[cell_num], dtype=np.float32)
            self.vbos.append(glvbo.VBO(data))

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
        self.program_active = False
        for widget in self.widgets:
            widget.closeEvent(QCloseEvent)

    def run(self):
        while self.program_active:
            processing = False
            for widget in self.widgets:
                if not widget.canvas.kd_tree_active:
                    processing = True
                    break
            if processing:
                self.statusBar().showMessage("Processing")
            else:
                self.statusBar().showMessage("Ready")

            time.sleep(.25)


class GLPlotWidget(QGLWidget, threading.Thread):
    """
    Anything here is just for the plot objects
    """

    def __init__(self, viewer, parent=None):
        QGLWidget.__init__(self)
        threading.Thread.__init__(self)

        self.program_active = True
        self.mouse_origin = 0
        self.alpha = .2
        self.mouse_pos = None

        self.x_ticks = 0
        self.y_ticks = 0

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
        self.ratio = 0
        self.orig_kd_tree = None
        self.lock = thread.allocate_lock()
        self.parent = parent

        # Starts the thread of anything inside of the run() method
        self.start()

    def recreate_kd_tree(self):
        if (self.width == 0) or (self.height == 0):
            return
        with self.lock:
            self.ratio = float(self.height) / float(self.width)
            self.scale_x = float(self.view.width())
            self.scale_y = float(self.view.height())

            # highlighting using the kd_tree method being iterated over time
            for dset in self.data_sets:
                _data = np.array(dset.getFilteredDataSet(self.view.view()), copy=True)
                # In case the data-size is empty after filtering
                if _data.size == 0:
                    continue

                _data[:, 0] /= (self.scale_x * self.ratio)
                _data[:, 1] /= self.scale_y
                self.kd_tree.append(
                    KDTreeWritable(dset.getTitle(), _data[:, 0:2], leafsize=100, use_cache_data=False).load()
                )

            if self.orig_kd_tree is None:
                self.orig_kd_tree = self.kd_tree

            print "kd_tree complete for " + self.title
            self.kd_tree_active = True

    def run(self):
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
    def draw_axes(self):
        gl.glLineWidth(2.5)
        self.qglColor(QtCore.Qt.black)
        left, bottom, z_ = glu.gluUnProject(0, 0, 0)
        right, top, z_ = glu.gluUnProject(self.width, self.height, 0)
        gl.glBegin(gl.GL_LINES)
        # Bottom
        gl.glVertex3f(left, bottom, 0)
        gl.glVertex3f(right, bottom, 0)
        # Right
        gl.glVertex3f(right, bottom, 0)
        gl.glVertex3f(right, top, 0)
        # Top
        gl.glVertex3f(left, top, 0)
        gl.glVertex3f(right, top, 0)
        # Left
        gl.glVertex3f(left, bottom, 0)
        gl.glVertex3f(left, top, 0)
        gl.glEnd()

        self.draw_axes_ticks(left, right, bottom, top, self.x_ticks, self.y_ticks)

        x_, y_, z_ = glu.gluUnProject(0, 50, 0)
        # self.renderText(x_, y_, 0.0, "Multisampling disabled", self.font())

    def draw_axes_ticks(self, left, right, bottom, top, num_ticks_x, num_ticks_y):
        tick_width = 5
        x_, y_, z_ = glu.gluUnProject(tick_width, tick_width, 0)
        dx = (right - left) / (num_ticks_x - 1)
        dy = (top - bottom) / (num_ticks_y - 1)

        gl.glLineWidth(1)
        gl.glBegin(gl.GL_LINES)
        # Draw number ticks in x direction
        for x in range(num_ticks_x):
            gl.glVertex3f(x * dx + left, bottom, 0)
            gl.glVertex3f(x * dx + left, y_, 0)
        for y in range(num_ticks_y):
            gl.glVertex3f(left, y * dy + bottom, 0)
            gl.glVertex3f(x_, y * dy + bottom, 0)
        gl.glEnd()

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

        x_ /= (self.scale_x * self.ratio)
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
        return tree_num, pt_num, d, focus_x * self.scale_x * self.ratio, focus_y * self.scale_y

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
        gl.glMatrixMode(gl.GL_MODELVIEW)
        for dSet in self.data_sets:
            # set blue color for subsequent drawing rendering calls
            dSet.getColor(self.alpha)
            gl.glPushMatrix()
            dSet.getTranslation()
            # bind the VBO
            vbo = dSet.getVBO()
            vbo.bind()
            # tell OpenGL that the VBO contains an array of vertices
            gl.glEnableClientState(gl.GL_VERTEX_ARRAY)
            # these vertices contain 2 single precision coordinates
            gl.glVertexPointer(2, gl.GL_FLOAT, 0, vbo)
            # draw "count" points from the VBO
            gl.glDrawArrays(gl.GL_POINTS, 0, dSet.count)
            vbo.unbind()
            gl.glPopMatrix()

        gl.glDisable(gl.GL_BLEND)

        if self.mouse_pos is not None and not self.rubberband.isVisible():
            self.draw_kd_tree_point()

        if self.rubberband.isVisible():
            self.rubberband.restrictBoundaries(self.width, self.height)
            self.rubberband.draw()

        gl.glDisable(gl.GL_BLEND)

        self.draw_axes()

        gl.glFlush()

    def resizeGL(self, width, height):
        """
        Called upon window resizing: reinitialize the viewport.
        """
        # update the window size
        self.width, self.height = width, height
        self.x_ticks = int(self.width / 80)
        self.y_ticks = int(self.height / 14)
        if self.y_ticks > 6:
            self.y_ticks = int(self.y_ticks / 2)
        self.setOrtho(self.view.view())
        print "Resizing"
        QGLWidget.resizeGL(self, width, height)

    def resetToOriginalView(self):
        print "Resetting to original view: " + str(self.view.orig_view)
        self.setOrtho(self.view.orig_view)
        self.view.set_view(self.view.orig_view)
        self.resetToOriginalKdTree()

    def resetToOriginalKdTree(self):
        with self.lock:
            self.kd_tree = self.orig_kd_tree
            self.ratio = float(self.height) / float(self.width)
            self.scale_x = float(self.view.width())
            self.scale_y = float(self.view.height())

    def closeEvent(self, QCloseEvent):
        print "closeEvent called for " + self.title
        self.program_active = False

        QGLWidget.closeEvent(self, QCloseEvent)


def convertMousePoint2DrawPlane(event_pos, height):
    return QtCore.QPoint(event_pos.x(), height - event_pos.y())


class GLUIWidget(UI, GLPlotWidget):
    """
    Widget class for the three cell plots. Called in GuiCellPlot. Inherits from GLPlotWidget
    """

    def __init__(self, viewer, parent=None):
        GLPlotWidget.__init__(self, viewer, parent=parent)

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
            self.parentWidget().repaint()
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
            self.parentWidget().repaint()
        else:
            self.view.set_view(self.prevView)
            self.repaint()
            self.parentWidget().repaint()
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
            self.parentWidget().repaint()

        self.repaint()
        GLPlotWidget.mouseMoveEvent(self, event)


def convertLabel(value):
    value = round(value, 2)
    if (value * 100) % 100 == 0:
        value = int(value)
    return str(value)


class FigureDiagramWidget(QWidget):
    def __init__(self, viewer):
        QWidget.__init__(self)

        self.height = 0
        self.width = 0
        self.padding_left = 60
        self.padding_bottom = 20

        boxy = QtGui.QVBoxLayout(self)
        self.setLayout(boxy)
        # self.setFixedSize(self.width, self.height)
        self.canvas = GLUIWidget(viewer, parent=self)
        self.layout().addWidget(self.canvas)
        self.metrics = QtGui.QFontMetrics(self.font())
        self.layout().setContentsMargins(self.padding_left, self.metrics.height() / 2, 30, self.padding_bottom)

    def paintEvent(self, QPaintEvent):
        self.height = self.canvas.height
        self.width = self.canvas.width
        painter = QtGui.QPainter()
        view = self.canvas.view.view()
        painter.begin(self)
        self.drawXLabels(painter, view[0], view[1], self.canvas.x_ticks)
        self.drawYLabels(painter, view[2], view[3], self.canvas.y_ticks)
        painter.end()

    def drawYLabels(self, painter, start, end, num_ticks):
        for i in range(num_ticks):
            value = i * (end - start) / (num_ticks - 1) + start
            label = convertLabel(value)
            label_width = self.metrics.width(label)
            pos = i * self.height / (num_ticks - 1)
            painter.drawText(self.padding_left - label_width - 5, self.height - pos, label_width, 100, 0, label)

    def drawXLabels(self, painter, start, end, num_ticks):
        for i in range(num_ticks):
            value = i * (end - start) / (num_ticks - 1) + start
            label = convertLabel(value)
            label_width = self.metrics.width(label)
            pos = i * self.width / (num_ticks - 1)
            painter.drawText(pos - label_width / 2 + self.padding_left, self.height + self.metrics.height() + 10, label)

    def closeEvent(self, QCloseEvent):
        self.canvas.closeEvent(QCloseEvent)
        QWidget.closeEvent(self, QCloseEvent)