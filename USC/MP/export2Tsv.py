import numpy as np

__author__ = 'mavinm'

already_rendered_file = "parallelData.bin"

f = file(already_rendered_file, "rb")
MEA_data = np.load(f)
LEA_data = np.load(f)
GC_data = np.load(f)
BC_data = np.load(f)
f.close()