from PyQt4 import QtGui
from modules import GLPlotWidget, CellTypeDataSet

__author__ = 'mavinm'


# define a QT window with an OpenGL widget inside it
class MEA_LEA_Window(QtGui.QMainWindow):
    def __init__(self, MEA_data, LEA_data, view):
        super(MEA_LEA_Window, self).__init__()
        # generate random data points
        # initialize the GL widget
        set1 = CellTypeDataSet(MEA_data, rgb=(0, 0, 1))
        set2 = CellTypeDataSet(LEA_data, rgb=(1, 0, 0))
        dataSets = (set1, set2)
        self.widget = GLPlotWidget(dataSets, view)
        # put the window at the screen position (100, 100)
        self.setGeometry(100, 100, self.widget.width, self.widget.height)
        self.setCentralWidget(self.widget)

        self.show()


class Position_Window(QtGui.QMainWindow):
    def __init__(self, data, view, rgb=(0, 0, 0)):
        super(Position_Window, self).__init__()
        # generate random data points
        # initialize the GL widget
        set1 = CellTypeDataSet(data, rgb=rgb)
        dataSets = (set1,)
        self.widget = GLPlotWidget(dataSets, view)
        # put the window at the screen position (100, 100)
        self.setGeometry(100, 100, self.widget.width, self.widget.height)
        self.setCentralWidget(self.widget)

        self.show()
