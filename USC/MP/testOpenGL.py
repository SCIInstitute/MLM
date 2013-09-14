# PyQT4 imports
from PyQt4 import QtGui, QtCore, QtOpenGL
from PyQt4.QtGui import QHBoxLayout
from PyQt4.QtOpenGL import QGLWidget
# PyOpenGL imports
import OpenGL.GL as gl
import OpenGL.arrays.vbo as glvbo


class CellTypeDataSet():
    """
    Set's The data type set into this object
    dataSet must be a tuple (dataSet,)
    """

    def __init__(self, dataSet, rgb=(1, 1, 1), xyz=(0, 0, 0)):
        # create a Vertex Buffer Object with the specified data
        self.vbo = glvbo.VBO(dataSet)
        self.count = dataSet.shape[0]
        self.rgb = rgb
        self.xyz = xyz

    def setTranslation(self, x, y, z):
        self.xyz = (x, y, z)

    def setColor(self, r, g, b):
        self.rgb = (r, g, b)

    def getTranslation(self):
        return gl.glTranslate(self.xyz[0], self.xyz[1], self.xyz[2])

    def getColor(self):
        return gl.glColor(self.rgb[0], self.rgb[1], self.rgb[2])

    def getVBO(self):
        return self.vbo


class GLPlotEAWidget(QGLWidget):
    # default window size
    width, height = 600, 600

    def __init__(self, dataSets, view=(0,1,0,1)):
        super(GLPlotEAWidget, self).__init__()

        self.dataSets = dataSets
        self.tStart = view[0]
        self.tStop = view[1]
        self.rangeBot = view[2]
        self.rangeTop = view[3]

    def set_view_size(self, tStart, tStop, rangeBot, rangeTop):
        """Set's the size of the view space
        """
        self.tStart = tStart
        self.tStop = tStop
        self.rangeBot = rangeBot
        self.rangeTop = rangeTop


    def initializeGL(self):
        """Initialize OpenGL, VBOs, upload data on the GPU, etc.
        """
        # background color
        gl.glClearColor(0, 0, 0, 0)

    def paintGL(self):
        """Paint the scene.
        """
        # clear the buffer
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        for dSet in self.dataSets:
            # set blue color for subsequent drawing rendering calls
            dSet.getColor()
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

    def resizeGL(self, width, height):
        """Called upon window resizing: reinitialize the viewport.
        """
        # update the window size
        self.width, self.height = width, height
        # paint within the whole window
        gl.glViewport(0, 0, width, height)
        # set orthographic projection (2D only)
        gl.glMatrixMode(gl.GL_PROJECTION)
        gl.glLoadIdentity()

        gl.glOrtho(self.tStart, self.tStop, self.rangeBot, self.rangeTop, -1, 1)

    def updateGL(self):
        for dSet in self.dataSets:
            dSet.getVBO()[0].x += 1
            pass

### TODO - THIS IS AN EXAMPLE OF MULTIPLE WIDGETS IN ONE WINDOW
# class GLPlotEAWidget(QGLWidget):
#     # default window size
#     width, height = 600, 600
#
#     def __init__(self):
#         super(GLPlotEAWidget, self).__init__()
#
#         self.layout = QHBoxLayout()
#         self.test1 = GLPlotEAWidget()
#         self.setLayout(self.layout)
#         self.layout.addWidget(self.test1)
#
#     def set_data(self, MEA_data, LEA_data):
#         """Load 2D data as a Nx2 Numpy array.
#         """
#         self.test1.set_data(MEA_data, LEA_data)
#
#     def set_view_size(self, tStart, tStop, rangeBot, rangeTop):
#         """Set's the size of the view space
#         """
#         self.test1.set_view_size(tStart, tStop, rangeBot, rangeTop)
#
#         self.tStart = tStart
#         self.tStop = tStop
#         self.rangeBot = rangeBot
#         self.rangeTop = rangeTop
#
#     def initializeGL(self):
#         """Initialize OpenGL, VBOs, upload data on the GPU, etc.
#         """
#         # background color
#         gl.glClearColor(0, 0, 0, 0)
#
#     def paintGL(self):
#         """Paint the scene.
#         """
#         # clear the buffer
#         gl.glClear(gl.GL_COLOR_BUFFER_BIT)
#
#     def resizeGL(self, width, height):
#         """Called upon window resizing: reinitialize the viewport.
#         """
#         # update the window size
#         self.width, self.height = width, height
#         # paint within the whole window
#         gl.glViewport(0, 0, width, height)
#         # set orthographic projection (2D only)
#         gl.glMatrixMode(gl.GL_PROJECTION)
#         gl.glLoadIdentity()
#
#         gl.glOrtho(self.tStart, self.tStop, self.rangeBot, self.rangeTop, -1, 1)


if __name__ == '__main__':
    # import numpy for generating random data points
    import sys
    import numpy as np
    import numpy.random as rdn

    # define a QT window with an OpenGL widget inside it
    class TestWindow(QtGui.QMainWindow):
        def __init__(self, data):
            super(TestWindow, self).__init__()
            # generate random data points
            self.data = data
            # initialize the GL widget
            set1 = CellTypeDataSet(self.data, rgb=(0, 0, 1))
            set2 = CellTypeDataSet(self.data, rgb=(1, 0, 0), xyz=(5, 0, 0))
            dataSets = (set1, set2)
            self.widget = GLPlotEAWidget(dataSets, (0, 10, 0, 10))
            # put the window at the screen position (100, 100)
            self.setGeometry(100, 100, self.widget.width, self.widget.height)
            self.setCentralWidget(self.widget)
            self.show()

    # create the QT App and window
    app = QtGui.QApplication(sys.argv)
    data = np.array(5 * rdn.random([5000, 2]), dtype=np.float32)
    window = TestWindow(data)
    window.show()
    app.exec_()