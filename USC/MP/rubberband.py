from view import Viewer
import OpenGL.GL as gl


class RectRubberband():
    def __init__(self):
        self.visible = False
        self.box = Viewer()

    def draw(self):
        gl.glLineWidth(2.5)
        gl.glColor3f(100, 0, 0)
        left, right, bottom, top = self.box.unprojectView()
        # Inverts the mouse pointer
        gl.glBegin(gl.GL_LINES)
        gl.glVertex2f(left, top)
        gl.glVertex2f(left, bottom)
        gl.glVertex2f(left, bottom)
        gl.glVertex2f(right, bottom)
        gl.glVertex2f(right, bottom)
        gl.glVertex2f(right, top)
        gl.glVertex2f(right, top)
        gl.glVertex2f(left, top)
        gl.glEnd()

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False

    def isVisible(self):
        return self.visible

    def setGeometry(self, event):
        self.box.set_view((event.left(), event.right(), event.bottom(), event.top()))

    def restrictBoundaries(self, width, height):
        print "(" + str(self.box.view()) + "," + str((width, height)) + ")"
        if self.box.left < 0:
            self.box.left = 0
        if self.box.right > width:
            self.box.right = width
        if self.box.top < 0:
            self.box.top = 0
        if self.box.bottom > height:
            self.box.bottom = height