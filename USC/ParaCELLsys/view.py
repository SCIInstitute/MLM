import OpenGL.GLU as glu
import math


__author__ = 'mavinm'


class Viewer():
    def __init__(self, *args, **kwargs):

        num_args = len(args)
        self.left = 0
        self.right = 0
        self.bottom = 0
        self.top = 0

        self.orig_view = None

        if num_args == 0:
            self.__initializeView((0, 1, 0, 1))
        elif num_args == 1:
            self.__initializeView(args[0])
        elif num_args == 4:
            self.__initializeView((args[0], args[1], args[2], args[3]))
        else:
            raise KeyError("You did not meet the Viewer() initialization criteria")

    def __initializeView(self, view):
        self.set_view((float(view[0]), float(view[1]), float(view[2]), float(view[3])))

        self.orig_view = (float(view[0]), float(view[1]), float(view[2]), float(view[3]))
        self.orig_point_size = self.point_size()

    def view(self):
        return self.left, self.right, self.bottom, self.top, self.point_size()

    def leftTop(self):
        return self.left, self.top

    def rightTop(self):
        return self.right, self.top

    def leftBottom(self):
        return self.left, self.bottom

    def rightBottom(self):
        return self.right, self.bottom

    def set_view(self, view):
        self.left = float(view[0])
        self.right = float(view[1])
        self.bottom = float(view[2])
        self.top = float(view[3])

    def width(self):
        return self.right - self.left

    def height(self):
        return self.top - self.bottom

    def perimeter(self):
        return 2 * self.height() + 2 * self.width()

    def point_size(self):
        p = self.perimeter()
        if p > 2000:
            return 1
        elif 2000 >= p > 900:
            return 2
        elif 900 >= p > 100:
            return 3
        elif 100 >= p > 50:
            return 4
        else:
            return 5

    def reset_view(self):
        self.left, self.right, self.bottom, self.top = self.orig_view

    def unprojectView(self):
        _left, _bottom, z = glu.gluUnProject(self.left, self.bottom, 0.0)
        _right, _top, z = glu.gluUnProject(self.right, self.top, 0.0)

        # Not sure why but I had to switch the bottom and top or the vertices flipped
        return _left, _right, _top, _bottom

    def dataDistance(self):
        left, right, top, bottom = self.unprojectView()
        # Returns distance from bottom-left to top-right
        return math.hypot(left - right, top - bottom)


class ViewTile():
    """
    Keeps Track of the data sets along with window information like view size, etc.

    data_set : CellTypeDataSet(dataSet, rgb, xyz) # Cell Data being read in
    view     : (x_left, x_right, y_bottom, y_top, perimeter) # The window sizes to show the data
    """

    def __init__(self, data_set, view):
        self.title = ""
        self.data_set = data_set
        self.view = Viewer(view)

        for data in data_set:
            self.title += data.getTitle()

    def get_Data(self):
        return self.data_set

    def get_View(self):
        return self.view

    def get_Title(self):
        return self.title
