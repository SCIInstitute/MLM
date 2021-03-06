from enum import Enum
import math
import OpenGL.GL as gl
import OpenGL.GLU as glu
from PyQt4.QtGui import QWidget, QMessageBox

__author__ = 'mavin martin'


class Tools(Enum):
    NONE = 0
    ZOOM_IN = 1
    SCALING = 2


class Callbacks(Enum):
    NONE = 0
    RESIZE = 1
    CLICK = 2
    RESET = 3


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class ToolQB():
    __metaclass__ = Singleton

    def zoom_in(self, mouse, parent=None):
        if self.prev_position_rect is None:
            self.prev_position_rect = mouse.pos()
        else:
            current_position = mouse.pos()
            prev_xy = (self.prev_position_rect.x(), self.prev_position_rect.y())
            curr_xy = (current_position.x(), current_position.y())
            dist = math.hypot(curr_xy[0] - prev_xy[0],
                              curr_xy[1] - prev_xy[1])

            if dist < 2:
                #print "Treat as a click"
                callback = Callbacks.CLICK
            elif abs(curr_xy[0] - prev_xy[0]) < 2 or abs(curr_xy[1] - prev_xy[1]) < 2:
                QMessageBox.about(parent, "ERROR", "Your view window is too small to compute.")
                callback = Callbacks.RESET
            else:
                #print "Zoom in"
                callback = Callbacks.RESIZE
            self.prev_position_rect = None

            return callback

    def scale(self, mouse, mouse_release, window_height=None, view=None):

        if view is not None:
            self.orig_view_scale = view
            print('view', view)
            print view

        """
        Scales the window according to movement
        mouse - Mouse Event passed in
        mouse_release - Boolean representing release
        """
        if self.prev_position_scale is None:
            self.prev_position_scale = mouse.pos()
            x, y, z = glu.gluUnProject(mouse.pos().x(), window_height - mouse.pos().y(), 0.0)
            self.anchor_position_scale = x, y
        elif not mouse_release:
            current_position = mouse.pos()
            return current_position.x() - self.prev_position_scale.x()
        else:
            #print "Mouse scaling released"
            current_position = mouse.pos()
            prev_xy = (self.prev_position_scale.x(), self.prev_position_scale.y())
            curr_xy = (current_position.x(), current_position.y())
            dist = math.hypot(curr_xy[0] - prev_xy[0],
                              curr_xy[1] - prev_xy[1])
            if dist < 2:
                #print "Treat as a click"
                callback = Callbacks.CLICK
            else:
                #print "Zoom in"
                callback = Callbacks.RESIZE

            self.prev_position_scale = None
            self.anchor_position_scale = None
            self.orig_view_scale = None

            return callback

    def mouse_down(self, mouse, tool, window_height=None, view=None):
        if tool == Tools.ZOOM_IN:
            self.zoom_in(mouse)
        elif tool == Tools.SCALING:
            self.scale(mouse, False, window_height, view)

    def get_orig_view_scale(self):
        return self.orig_view_scale

    def mouse_up(self, mouse, tool, parent=None):
        if tool == Tools.ZOOM_IN:
            return self.zoom_in(mouse, parent)
        elif tool == Tools.SCALING:
            return self.scale(mouse, True)

    def mouse_move(self, mouse, tool):
        if tool == Tools.SCALING:
            return self.scale(mouse, False)

    def scaling_in_effect(self):
        """
        Returns boolean
        """
        return self.prev_position_scale is not None

    def get_scale_anchor(self):
        """
        Returns the on-click position when wanting to scale
        """
        return self.anchor_position_scale

    def __init__(self):
        self.tool = Tools.ZOOM_IN
        self.prev_position_rect = None
        self.prev_position_scale = None
        self.anchor_position_scale = None
        self.orig_view_scale = None
