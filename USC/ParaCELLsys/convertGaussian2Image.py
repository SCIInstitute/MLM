import numpy as np
import Image

__author__ = 'mavinm'
__date__ = '3/21/14'


def rescale_data_to_image(data):
    # data = data **
    return (255.0 / data.max() * (data - data.min())).astype(np.uint8)

if __name__ == "__main__":
    filenames = {
        "tmp/bc_data_gaussian_sigma=0.001.bin": "report/bc_gaussian-0.001.png",
        "tmp/bc_data_gaussian_sigma=0.002.bin": "report/bc_gaussian-0.002.png",
        "tmp/bc_data_gaussian_sigma=0.003.bin": "report/bc_gaussian-0.003.png",
        "tmp/bc_data_gaussian_sigma=0.004.bin": "report/bc_gaussian-0.004.png",

        "tmp/gc_data_gaussian_sigma=0.001.bin": "report/gc_gaussian-0.001.png",
        "tmp/gc_data_gaussian_sigma=0.002.bin": "report/gc_gaussian-0.002.png",
        "tmp/gc_data_gaussian_sigma=0.003.bin": "report/gc_gaussian-0.003.png",
        "tmp/gc_data_gaussian_sigma=0.004.bin": "report/gc_gaussian-0.004.png",

        "tmp/mea_lea_data_gaussian_sigma=0.001.bin": "report/mea_lea_gaussian-0.001.png",
        "tmp/mea_lea_data_gaussian_sigma=0.002.bin": "report/mea_lea_gaussian-0.002.png",
        "tmp/mea_lea_data_gaussian_sigma=0.003.bin": "report/mea_lea_gaussian-0.003.png",
        "tmp/mea_lea_data_gaussian_sigma=0.004.bin": "report/mea_lea_gaussian-0.004.png",
    }

    for fn, out in filenames.iteritems():
        data = np.load(fn)
        sigma = fn.split("=")[1].rstrip(".bin")
        print sigma
        rescaled = rescale_data_to_image(data)
        im = Image.fromarray(rescaled)
        im.save(out)