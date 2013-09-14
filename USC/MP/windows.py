from PyQt4 import QtGui
from modules import GLPlotWidget, CellTypeDataSet

from random import random
from PyQt4 import QtCore

from guiqwt.plot import CurvePlot
from guiqwt.builder import make

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

    def __setup_layout(self):
        self.connect(self.button, QtCore.SIGNAL('clicked()'), self.button_Click)

        # Create the curves
        self.curveA = make.curve([], [], 'curveA', QtGui.QColor(255, 0, 0))
        self.curveB = make.curve([], [], 'curveB', QtGui.QColor(0, 255, 0))
        self.curveC = make.curve([], [], 'curveC', QtGui.QColor(0, 0, 255))
        self.plot.add_item(self.curveA)
        self.plot.add_item(self.curveB)
        self.plot.add_item(self.curveC)

    def button_Click( self ):
        self.curveA.set_data(range(0, 20, 2), map(lambda _: random(), range(0, 10)))
        self.curveB.set_data(range(0, 20, 2), map(lambda _: random() + random(), range(0, 10)))
        self.curveC.set_data(range(0, 20, 2), map(lambda _: random() + random() + random(), range(0, 10)))
        self.plot.replot()



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
