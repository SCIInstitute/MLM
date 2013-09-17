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

        g_box = QtGui.QGridLayout()
        g_box.setSpacing(10)
        g_box.addWidget(bc_widget, 1, 0)
        g_box.addWidget(gc_widget, 2, 0, 5, 0)
        g_box.addWidget(mea_lea_widget, 7, 0, 2, 0)

        w = QtGui.QWidget()
        w.setLayout(g_box)

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