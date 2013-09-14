from PyQt4 import QtGui
from PyQt4.QtGui import QHBoxLayout
from testOpenGL import GLPlotEAWidget

__author__ = 'mavinm'

# define a QT window with an OpenGL widget inside it
class MEA_LEA_Window(QtGui.QMainWindow):
    def __init__(self, MEA_data, LEA_data, tstart, tstop, cellStart, cellStop):
        super(MEA_LEA_Window, self).__init__()
        # generate random data points
        # initialize the GL widget
        self.widget = GLPlotEAWidget()
        self.widget.set_data(MEA_data, LEA_data)
        self.widget.set_view_size(tstart, tstop, cellStart, cellStop)
        # put the window at the screen position (100, 100)
        self.setGeometry(100, 100, self.widget.width, self.widget.height)
        self.setCentralWidget(self.widget)

        self.show()