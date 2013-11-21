from enum import Enum
import math

__author__ = 'mavin martin'



class Tools(Enum):
    NONE = 0
    ZOOM_IN = 1


class Callbacks(Enum):
    NONE = 0
    RESIZE = 1
    CLICK = 2


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class ToolQB():

    __metaclass__ = Singleton

    def zoom_in(self, mouse):
        if self.prev_position is None:
            self.prev_position = mouse.pos()
        else:
            current_position = mouse.pos()
            prev_xy = (self.prev_position.x(), self.prev_position.y())
            curr_xy = (current_position.x(), current_position.y())
            dist = math.hypot(curr_xy[0] - prev_xy[0],
                              curr_xy[1] - prev_xy[1])
            if dist < 2:
                print "Treat as a click"
                callback = Callbacks.CLICK
            else:
                print "Zoom in"
                callback = Callbacks.RESIZE
            self.prev_position = None

            return callback

    options = {
        Tools.ZOOM_IN: zoom_in,
    }

    def mouse_down(self, mouse):
        self.options[self.tool](self, mouse)

    def mouse_up(self, mouse):
        return self.options[self.tool](self, mouse)

    def __init__(self):
        self.tool = Tools.ZOOM_IN
        self.prev_position = None