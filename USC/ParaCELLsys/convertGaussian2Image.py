import numpy as np
import Image
from gaussian_gpu import GpuGridGaussian
from models import ParseParallelCellData, CellTypeDataSet
from view import ViewTile

__author__ = 'mavinm'
__date__ = '3/21/14'


def rescale_data_to_image(data):
    return (255.0 / data.max() * (data - data.min())).astype(np.uint8)

if __name__ == "__main__":
    filenames = (
        "tmp/gc_data_gaussian_sigma=0.2.bin",
        "tmp/gc_data_gaussian_sigma=0.4.bin",
        "tmp/gc_data_gaussian_sigma=0.6.bin",
        "tmp/gc_data_gaussian_sigma=0.8.bin",
        "tmp/gc_data_gaussian_sigma=1.0.bin"
    )

    for fn in filenames:
        data = np.load(fn)
        sigma = fn.split("=")[1].rstrip(".bin")
        print sigma
        rescaled = rescale_data_to_image(data)
        im = Image.fromarray(rescaled)
        im.save("report/gc_gaussian-"+str(sigma)+".png")