import sys
from random import random
from PyQt4 import QtCore, QtGui

from guiqwt.plot import CurvePlot
from guiqwt.builder import make


class GuiQwtPlot(QtGui.QMainWindow):
    def __init__(self):
        QtGui.QMainWindow.__init__(self)
        self.__create_layout()
        self.__setup_layout()

    def __create_layout( self ):
        self.setWindowTitle('LambdaFunction - guiqwt')

        self.plot = CurvePlot(self)
        # self.plot.set_antialiasing(True)
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

    def button_Click(self):
        self.curveA.set_data(range(0, 20, 2), map(lambda _: random(), range(0, 10)))
        self.curveB.set_data(range(0, 20, 2), map(lambda _: random() + random(), range(0, 10)))
        self.curveC.set_data(range(0, 20, 2), map(lambda _: random() + random() + random(), range(0, 10)))
        self.plot.replot()


def main():
    app = QtGui.QApplication(sys.argv)
    prog = GuiQwtPlot()
    prog.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()