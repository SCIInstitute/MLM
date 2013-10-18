from PyQt4 import QtGui, QtCore
import OpenGL.GL as gl
from PyQt4.QtOpenGL import QGLWidget
from view import CustomRubberband


class Window(QGLWidget):
    def __init__(self):
        QtGui.QWidget.__init__(self)
        self.rubberband = CustomRubberband()
        self.setMouseTracking(True)

    def paintGL(self):
        gl.glClear(gl.GL_COLOR_BUFFER_BIT)

        print "Yes"

    def initializeGL(self):
        gl.glClearColor(1, 1, 1, 1)

    def mousePressEvent(self, event):
        self.origin = event.pos()
        self.rubberband.setGeometry(
            QtCore.QRect(self.origin, QtCore.QSize()))
        self.rubberband.show()
        QtGui.QWidget.mousePressEvent(self, event)

    def mouseMoveEvent(self, event):
        if self.rubberband.isVisible():
            self.rubberband.setGeometry(
                QtCore.QRect(self.origin, event.pos()).normalized())
        QtGui.QWidget.mouseMoveEvent(self, event)

    def mouseReleaseEvent(self, event):
        if self.rubberband.isVisible():
            self.rubberband.hide()
            #selected = []
            #rect = self.rubberband.geometry()
            #for child in self.findChildren(QtGui.QPushButton):
            #    if rect.intersects(child.geometry()):
            #        selected.append(child)
            #print 'Selection Contains:\n ',
            #if selected:
            #    print '  '.join(
            #        'Button: %s\n' % child.text() for child in selected)
            #else:
            #    print ' Nothing\n'
        QtGui.QWidget.mouseReleaseEvent(self, event)


if __name__ == '__main__':
    import sys

    app = QtGui.QApplication(sys.argv)
    window = Window()
    window.show()
    sys.exit(app.exec_())