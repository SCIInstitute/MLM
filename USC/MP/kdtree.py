import cPickle
from scipy.spatial import kdtree


class KDTreeWritable(kdtree.KDTree):
    """
    This is a hack found at http://stackoverflow.com/questions/5773216/saving-kdtree-object-in-python
    It allows you to write the data to a file
    """
    def __init__(self, data, leafsize = 10):
        kdtree.node = kdtree.KDTree.node
        kdtree.leafnode = kdtree.KDTree.leafnode
        kdtree.innernode = kdtree.KDTree.innernode

        kdtree.KDTree.__init__(self, data, leafsize)

    def writeFile(self, filename):
        self.test = cPickle.dump(self, open("tmp/test.bin", "wb"))

    """
    Used to store a previous kd tree into a variable
    """
    def readFile(self, filename):
        return cPickle.loads(self.test)