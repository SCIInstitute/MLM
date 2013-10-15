from PyQt4 import QtGui
from PyQt4.QtGui import QWidget
from modules import GLPlotWidget, CellTypeDataSet

from PyQt4 import QtCore

__author__ = 'mavinm'


class GuiCellPlot(QtGui.QMainWindow):
    width = 800
    height = 500
    """
    Plots all of the cells in one graph
    """

    def __init__(self, mea_lea_tile, gc_tile, bc_tile):
        super(GuiCellPlot, self).__init__()
        self.central = QWidget(self)

        mea_lea_widget = GLPlotWidget(mea_lea_tile.data_set, mea_lea_tile.view)
        gc_widget = GLPlotWidget(gc_tile.data_set, gc_tile.view)
        bc_widget = GLPlotWidget(bc_tile.data_set, bc_tile.view)

        self.grid = QtGui.QGridLayout(self.central)
        self.grid.setSpacing(10)
        # TODO - Need to focus on the widget when multiple widgets in place
        self.grid.addWidget(bc_widget, 1, 0)
        self.grid.addWidget(gc_widget, 2, 0, 5, 0)
        self.grid.addWidget(mea_lea_widget, 7, 0, 2, 0)

        self.resize(self.width, self.height)
        self.setWindowTitle("Cell Plot")

        self.setCentralWidget(self.central)


class WindowTile():
    """
    Keeps Track of the data sets along with window information like view size, etc.

    data_set : CellTypeDataSet(dataSet, rgb, xyz) # Cell Data being read in
    view     : (x_left, x_right, y_bottom, y_top) # The window sizes to show the data
    """

    def __init__(self, data_set, view):
        self.data_set = data_set
        self.view = view