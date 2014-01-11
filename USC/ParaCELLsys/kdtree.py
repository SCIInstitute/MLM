import cPickle
import os
from scipy.spatial import kdtree as _kd
import zlib
import re


class KDTreeWritable(_kd.KDTree):
    """
    MAKE SURE TO CALL '''KDTreeWritable.load()'''.  If you know how to set self to the new class, we can change the method.  Not sure how to yet

    This is a hack found at http://stackoverflow.com/questions/5773216/saving-kdtree-object-in-python
    I have combined the code with http://stackoverflow.com/questions/12381471/how-to-load-all-cpickle-dumps-from-a-log-file
    It allows you to write the data to a file
    """

    rendered_file = "tmp/kdtree_"

    def __init__(self, title, data, leafsize=10, use_cache_data=False):
        self.title = title
        self.data = data
        self.leafsize = leafsize
        self.use_cache_data = use_cache_data

        self.rendered_file += re.sub(r'[^a-zA-Z\[\]]', '', title) + ".bin"

        _kd.node = _kd.KDTree.node
        _kd.leafnode = _kd.KDTree.leafnode
        _kd.innernode = _kd.KDTree.innernode

        if not use_cache_data:
            _kd.KDTree.__init__(self, data, leafsize)
            self.writeFile()

    def writeFile(self):
        dir = self.rendered_file.split('/')
        if not os.path.exists(dir[-2]):
            os.mkdir(dir[-2])
        f = open(self.rendered_file, "wb")
        f.write(zlib.compress(cPickle.dumps(self, cPickle.HIGHEST_PROTOCOL), 9))
        f.close()

    """
    Used to store a previous kd tree into a variable
    """

    def readCachedFile(self):
        if not os.path.isfile(self.rendered_file):
            _kd.KDTree.__init__(self, self.data, self.leafsize)
            self.writeFile()
            return self
        f = open(self.rendered_file, 'rb')
        data = cPickle.loads(zlib.decompress(f.read()))
        f.close()
        return data

    def load(self):
        if self.use_cache_data:
            return self.readCachedFile()
        else:
            return self