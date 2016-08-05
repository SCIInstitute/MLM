import threading
import thread
import time
import os

from PyQt4 import QtOpenGL
from PyQt4 import QtGui
from PyQt4.QtGui import QWidget, QMessageBox
from PyQt4 import QtCore
from PyQt4.QtOpenGL import QGLWidget
import OpenGL.GL as gl
import OpenGL.GLU as glu
import OpenGL.arrays.vbo as glvbo
import numpy as np
from os import path

from kdtree import KDTreeWritable
from models import rescale_data_to_image
from rubberband import RectRubberband
from tools import ToolQB, Callbacks, Tools
from ui import UI


__author__ = 'Mavin Martin'


class GuiCellPlot(QtGui.QMainWindow, threading.Thread):
    """
    Singleton: plots all of the cells in one graph and is called in main.
    """

    # The default height of the window
    width = 1200
    height = 800

    def __init__(self, mea_lea_tile, gc_tile, bc_tile, cell_hierarchy={}):
        super(GuiCellPlot, self).__init__()
        threading.Thread.__init__(self)
        self.central = QWidget(self)
        self.setCentralWidget(self.central)
        self.ui_widget = None

        # Makes the widget size not resizable
        self.setFixedSize(self.width, self.height)

        self.show_height_map = False #need cuda

        # all three plots as widgets with separate labels.
        # We want these as separate blocks so we can have axis and things
        # TODO - The named files are passed in to show images of what was computed using computeCellGaussian, needs to
        # TODO - change in the future
        mea_lea_widget = FigureDiagramWidget(mea_lea_tile, self.show_height_map,"data/mea_lea_data_gaussian_sigma=0.001.bin",show_time_title=True)
        gc_widget = FigureDiagramWidget(gc_tile, self.show_height_map, "data/gc_data_gaussian_sigma=0.001.bin")
        bc_widget = FigureDiagramWidget(bc_tile, self.show_height_map, "data/bc_data_gaussian_sigma=0.001.bin")

        self.widgets = (bc_widget, gc_widget, mea_lea_widget)

        self.boxy = QtGui.QVBoxLayout(self.central)

        # add all the plot widgets and labels to the layout
        self.boxy.addWidget(bc_widget, 2)
        self.boxy.addWidget(gc_widget, 8)
        self.boxy.addWidget(mea_lea_widget, 4)

        self.statusBar().showMessage("Ready")

        self.resize(self.width, self.height)
        self.setWindowTitle("ParaCELLsys")

        self.program_active = True

        self.start()

        self.initUI()

        self.vbos = []
        for cell_num in cell_hierarchy:
            data = np.array(cell_hierarchy[cell_num], dtype=np.float32)
            self.vbos.append(glvbo.VBO(data))

    def set_ui_heightmap_widget(self, widget):
        self.ui_widget = widget
        if self.show_height_map:
            self.ui_widget.show()
        else:
            self.ui_widget.hide()

    def initUI(self):
        menubar = self.menuBar()
        viewMenu = menubar.addMenu('&View')
        helpMenu = menubar.addMenu('&Help')

        # Tutorial
        tutorialAction = QtGui.QAction('&Tutorial', self)
        tutorialAction.setShortcut('Ctrl+T')
        tutorialAction.setStatusTip('Interaction Guide')
        tutorialAction.triggered.connect(self.tutorial)
        helpMenu.addAction(tutorialAction)

        # Height-Map Toggle
        heightAction = QtGui.QAction('&Height-map/Regular-view', self)
        heightAction.setShortcut('Ctrl+Y')
        heightAction.setStatusTip('Toggle between height-map and regular-view')
        heightAction.triggered.connect(self.toggle_height_map)
        viewMenu.addAction(heightAction)

    def tutorial(self):
        QMessageBox.about(self, "Tutorial",
                          "You can do many things inside of this application.  "
                          "Click on a cell to print the data results inside of the console window."
        )

    def toggle_height_map(self):
        self.show_height_map = not self.show_height_map
        for widget in self.widgets:
            widget.show_height_map = self.show_height_map
            widget.repaint()

    def keyPressEvent(self, QKeyEvent):
        print QKeyEvent.key()

    def closeEvent(self, QCloseEvent):
        self.program_active = False
        for widget in self.widgets:
            widget.closeEvent(QCloseEvent)

        if self.ui_widget is not None:
            self.ui_widget.close()

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


class UIWidget(QWidget):
    """
    Singleton: User interface that shows when height-map is enabled
    """
    width = 400
    height = 400

    def __init__(self, parent=None):
        # pass
        super(UIWidget, self).__init__()
        self.parent = parent
        self.resize(self.width, self.height)
        self.move(0, 0)

        # Makes the widget size not resizable
        # self.setFixedSize(self.width, self.height)

        self.setWindowTitle("Control Center")

        self.add_radio_buttons()

    def add_radio_buttons(self):
        layout = QtGui.QVBoxLayout(self)
        for widget in self.parent.widgets:
            r = QtGui.QCheckBox(widget.title.replace("\n", ""), self)
            layout.addWidget(r)
            r.setChecked(True)
            r.clicked.connect(widget.test_action, r.isChecked())


class GLPlotWidget(QGLWidget, threading.Thread):
    """
    Anything here is just for the plot objects
    """

    def __init__(self, viewer, parent, texture_file):
        QGLWidget.__init__(self)
        threading.Thread.__init__(self)

        self.texture_file = texture_file
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

    def initTexture(self):
        data = np.load(self.texture_file)
        data = rescale_data_to_image(data)
        w, h = data.shape

        # generate a texture id, make it current
        self.texture = gl.glGenTextures(1)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture)

        # texture mode and parameters controlling wrapping and scaling
        gl.glTexEnvf(gl.GL_TEXTURE_ENV, gl.GL_TEXTURE_ENV_MODE, gl.GL_MODULATE)
        gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_S, gl.GL_REPEAT)
        gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_WRAP_T, gl.GL_REPEAT)
        gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MAG_FILTER, gl.GL_LINEAR)
        gl.glTexParameterf(gl.GL_TEXTURE_2D, gl.GL_TEXTURE_MIN_FILTER, gl.GL_LINEAR)

        # map the image data to the texture. note that if the input
        # type is GL_FLOAT, the values must be in the range [0..1]
        gl.glTexImage2D(gl.GL_TEXTURE_2D, 0, gl.GL_RGB, w, h, 0,
                        gl.GL_LUMINANCE, gl.GL_UNSIGNED_BYTE, data)

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

        orig_view_scale = self.tool_qb.get_orig_view_scale()
        # Normalizes the vector, scales it, then puts it back into world coordinates
        l = (orig_view_scale[0] - mouse_pos[0]) * scale + mouse_pos[0]
        r = (orig_view_scale[1] - mouse_pos[0]) * scale + mouse_pos[0]
        b = (orig_view_scale[2] - mouse_pos[1]) * scale + mouse_pos[1]
        t = (orig_view_scale[3] - mouse_pos[1]) * scale + mouse_pos[1]

        self.view.set_view((l, r, b, t))
        self.setOrtho((l, r, b, t))

    # flesh this out- want to have it dynamically resize
    def draw_axes_markings(self):
        gl.glLineWidth(2.5)
        self.qglColor(QtCore.Qt.black)
        left, bottom, z_ = glu.gluUnProject(0, 0, 0)
        right, top, z_ = glu.gluUnProject(self.width, self.height, 0)
        gl.glBegin(gl.GL_LINES)
        # Bottom
        gl.glVertex2f(left, bottom)
        gl.glVertex2f(right, bottom)
        # Right
        gl.glVertex2f(right, bottom)
        gl.glVertex2f(right, top)
        # Top
        gl.glVertex2f(left, top)
        gl.glVertex2f(right, top)
        # Left
        gl.glVertex2f(left, bottom)
        gl.glVertex2f(left, top)
        gl.glEnd()

        self.draw_axes_ticks(left, right, bottom, top, self.x_ticks, self.y_ticks)

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
        if self.texture_file is not None and path.isfile(self.texture_file):
            self.initTexture()
        else:
            print "texture_file not found: ", self.texture_file

        #print "Open GL Version: " + gl.glGetString(gl.GL_VERSION)
        #print "Open GLSL Version: " + gl.glGetString(gl.GL_SHADING_LANGUAGE_VERSION)

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
        gl.glPointSize(self.view.view()[4])
        gl.glPopMatrix()
        gl.glDisable(gl.GL_POINT_SMOOTH)

    def drawDataPoints(self):
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

    def drawHeightMap(self):
        view = self.view.orig_view
        gl.glPushMatrix()
        gl.glColor3f(1, 1, 1)

        # enable textures, bind to our texture
        gl.glEnable(gl.GL_TEXTURE_2D)
        gl.glBindTexture(gl.GL_TEXTURE_2D, self.texture)

        gl.glBegin(gl.GL_QUADS)
        gl.glTexCoord2f(0, 0)
        gl.glVertex2f(view[0], view[2])

        gl.glTexCoord2f(1, 0)
        gl.glVertex2f(view[1], view[2])

        gl.glTexCoord2f(1, 1)
        gl.glVertex2f(view[1], view[3])

        gl.glTexCoord2f(0, 1)
        gl.glVertex2f(view[0], view[3])
        gl.glEnd()

        gl.glDisable(gl.GL_TEXTURE_2D)

        gl.glPopMatrix()

    def paintGL(self):
        """
        Paint the scene.
        """
        # clear the buffer
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)
        if self.parent.show_height_map and self.texture_file is not None:
            self.drawHeightMap()
        else:
            self.drawDataPoints()

        if self.mouse_pos is not None and not self.rubberband.isVisible():
            self.draw_kd_tree_point()

        if self.rubberband.isVisible():
            self.rubberband.restrictBoundaries(self.width, self.height)
            self.rubberband.draw()

        self.draw_axes_markings()

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
            self.y_ticks = int(self.y_ticks / 1.5)
        self.setOrtho(self.view.view())
        #print "Resizing"
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

    def __init__(self, viewer, parent, texture_file):
        GLPlotWidget.__init__(self, viewer, parent, texture_file)

    def mousePressEventLeft(self, event):
        print "Mouse Down Event"
        self.mouse_origin = convertMousePoint2DrawPlane(event.pos(), self.height)
        self.rubberband.setGeometry(
            QtCore.QRect(self.mouse_origin, QtCore.QSize()))
        self.rubberband.show()

        self.tool_qb.mouse_down(event, Tools.ZOOM_IN)

    def mousePressEventRight(self, event):
        self.tool_qb.mouse_down(event, Tools.SCALING, window_height=self.height, view=self.view.view())

    def mouseReleaseEventLeft(self, event):
        self.rubberband.hide()
        callback = self.tool_qb.mouse_up(event, Tools.ZOOM_IN, parent=self)
        if callback == Callbacks.RESIZE:
            print "Resizing"
            if self.rubberband.box.dataDistance() > .1:
                self.view.set_view(self.rubberband.box.unprojectView())
                self.setOrtho(self.view.view())
                print("point size: ",  self.view.view()[4])
                print("perimeter: ",  self.view.perimeter())
                gl.glPointSize(self.view.view()[4])
            else:
                QMessageBox.information(self, "ERROR", "Your view window is too small to compute.")
            self.kd_tree_active = False
            self.repaint()
            self.parentWidget().repaint()
        elif callback == Callbacks.CLICK:
            if not self.kd_tree_active:
                print "Data is still being evaluated, please wait"
                return
            print "data_pos :" + str(self.find_data_pos())
            tree_num, pt_num, distance, x, y = self.find_data_pos()
            print "Focus Point Number= " + str(pt_num)
            print "Distance from Mouse= " + str(distance)
            print "Point = (" + str(x) + ", " + str(y) + ")"

    def mouseReleaseEventRight(self, event):
        callback = self.tool_qb.mouse_up(event, Tools.SCALING)
        if callback == Callbacks.CLICK:
            self.resetToOriginalView()
            self.parentWidget().repaint()
            gl.glPointSize(self.view.view()[4])
        else:
            self.view.set_view(self.prevView)
            self.kd_tree_active = False
            self.repaint()
            self.parentWidget().repaint()
            gl.glPointSize(self.view.view()[4])

    def mouseMoveEvent(self, event):
        if self.rubberband.isVisible():
            self.rubberband.setGeometry(
                QtCore.QRect(self.mouse_origin, convertMousePoint2DrawPlane(event.pos(), self.height)).normalized())

        if self.tool_qb.scaling_in_effect():
            distance = self.tool_qb.mouse_move(event, Tools.SCALING)
            delta = distance / float(self.width)
            self.scaleOrtho(delta)
            self.parentWidget().repaint()
            gl.glPointSize(self.view.view()[4])

        self.repaint()
        GLPlotWidget.mouseMoveEvent(self, event)


def convertLabel(value):
    value = round(value, 2)
    if (value * 100) % 100 == 0:
        value = int(value)
    return str(value)


class FigureDiagramWidget(QWidget):
    def __init__(self, viewer, show_height_map, texture_file, show_time_title=False):
        QWidget.__init__(self)

        self.show_time_title = show_time_title
        self.height = 0
        self.width = 0
        self.padding_left = 100
        if self.show_time_title:
            self.padding_bottom = 50
        else:
            self.padding_bottom = 20

        self.title_font = QtGui.QFont()
        self.title_font.setPointSize(10)

        self.show_height_map = show_height_map

        boxy = QtGui.QVBoxLayout(self)
        self.setLayout(boxy)
        self.canvas = GLUIWidget(viewer, self, texture_file)
        self.title = self.canvas.title
        self.layout().addWidget(self.canvas)
        self.metrics = QtGui.QFontMetrics(self.font())
        self.title_metrics = QtGui.QFontMetrics(self.title_font)
        self.layout().setContentsMargins(self.padding_left, self.metrics.height() / 2, 30, self.padding_bottom)

    def test_action(self, checked):
        if checked:
            self.show()
        else:
            self.hide()

    def paintEvent(self, QPaintEvent):
        self.height = self.canvas.height
        self.width = self.canvas.width
        painter = QtGui.QPainter()
        view = self.canvas.view.view()
        painter.begin(self)
        self.drawXLabels(painter, view[0], view[1], self.canvas.x_ticks)
        self.drawYLabels(painter, view[2], view[3], self.canvas.y_ticks)
        painter.end()
        self.drawTitle(painter)

    def drawTitle(self, painter):
        painter.begin(self)
        painter.setFont(self.title_font)
        label_width = self.title_metrics.width(self.title)
        painter.translate(0, (self.height + label_width) / 2)
        painter.rotate(-90)
        painter.drawText(0, 0, label_width, 35, QtCore.Qt.TextWordWrap | QtCore.Qt.AlignCenter, self.title)
        painter.end()

        if self.show_time_title:
            painter.begin(self)
            painter.setFont(self.title_font)
            label = "Time (ms)"
            painter.drawText((self.width + self.title_metrics.width(label)) / 2, self.height + 50, label)
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
