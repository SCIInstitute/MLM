import numpy as np
from kdtree import KDTree

a = np.array([[1, 2, 3, 4, 5], [1, 2, 3, 4, 5]])
KDTree(a)
a = np.array([[3, 1, 5, 2, 4], [3, 1, 5, 2, 4]])
KDTree(a)
a = np.array([[5, 4, 3, 2, 1], [5, 4, 3, 2, 1]])
KDTree(a)
