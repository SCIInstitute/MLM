from PyQt4 import QtCore
from PyQt4.QtOpenGL import QGLWidget

__author__ = 'mavinm'


class UI(QGLWidget):

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.mousePressEventLeft(event)

        if event.button() == QtCore.Qt.RightButton:
            self.mousePressEventRight(event)

        QGLWidget.mousePressEvent(self, event)

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.mouseReleaseEventLeft(event)

        QGLWidget.mouseReleaseEvent(self, event)

    def mousePressEventRight(self, event):
        pass

    def mousePressEventLeft(self, event):
        pass

    def mouseReleaseEventLeft(self, event):
        pass

    def mouseReleaseEventRight(self, event):
        pass
