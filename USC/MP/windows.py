from PyQt4 import QtGui
from modules import GLPlotWidget, CellTypeDataSet

from PyQt4 import QtCore

__author__ = 'mavinm'


class GuiCellPlot(QtGui.QMainWindow):

    width = 800
    height = 500
    """
    Plots all of the cells in one graph
    """
    def __init__(self, MEA_LEA_TILE, GC_TILE, BC_TILE):
        super(GuiCellPlot, self).__init__()

        mea_lea_widget = GLPlotWidget(MEA_LEA_TILE.data_set, MEA_LEA_TILE.view)
        gc_widget = GLPlotWidget(GC_TILE.data_set, GC_TILE.view)
        bc_widget = GLPlotWidget(BC_TILE.data_set, BC_TILE.view)

        v_box = QtGui.QVBoxLayout()
        v_box.addWidget(bc_widget)
        v_box.addWidget(gc_widget)
        #v_box.addStretch(1)
        v_box.addWidget(mea_lea_widget)

        w = QtGui.QWidget()
        w.setLayout(v_box)

        self.resize(self.width, self.height)

        self.setCentralWidget(w)


class WindowTile():
    """
    Keeps Track of the data sets along with window information like view size, etc.

    data_set : CellTypeDataSet(dataSet, rgb, xyz) # Cell Data being read in
    view     : (x_left, x_right, y_bottom, y_top) # The window sizes to show the data
    """
    def __init__(self, data_set, view):
        self.data_set = data_set
        self.view = view


# define a QT window with an OpenGL widget inside it
class MEA_LEA_Window(QtGui.QMainWindow):
    def __init__(self, MEA_data, LEA_data, view):
        super(MEA_LEA_Window, self).__init__()
        # generate random data points
        # initialize the GL widget
        mea = CellTypeDataSet(MEA_data, rgb=(0, 0, 1))
        lea = CellTypeDataSet(LEA_data, rgb=(1, 0, 0))
        dataSets = (mea, lea)
        self.plot = GLPlotWidget(dataSets, view)
        # put the window at the screen position (100, 100)
        self.setGeometry(100, 100, self.plot.width, self.plot.height)

        self.setWindowTitle('LambdaFunction - guiqwt')

        self.button = QtGui.QPushButton('Load')

        ly = QtGui.QVBoxLayout()
        ly.addWidget(self.plot)
        ly.addWidget(self.button)

        w = QtGui.QWidget()
        w.setLayout(ly)

        self.setCentralWidget(w)

        self.connect(self.button, QtCore.SIGNAL('clicked()'), self.button_Click)

    def button_Click(self):
        print "Clicked Button"

class Position_Window(QtGui.QMainWindow):
    def __init__(self, data, view, rgb=(0, 0, 0)):
        super(Position_Window, self).__init__()
        # generate random data points
        # initialize the GL widget
        set1 = CellTypeDataSet(data, rgb=rgb)
        dataSets = (set1,)
        widget = GLPlotWidget(dataSets, view)
        # put the window at the screen position (100, 100)
        self.setGeometry(100, 100, widget.width, widget.height)
        self.setCentralWidget(widget)
