

class KDTree():
    """
    Currently dimensions to sort only works on 2d
    """
    def __init__(self, data, leafsize=10, dimensions_to_sort=-1):
        if dimensions_to_sort == -1:
            dimensions_to_sort = data.shape[1]

        print data

    # 0 - x
    # 1 - y
    # 2 - z
    def quicksort(self, axis):
        pass

    def query(self, point):
        raise NotImplementedError