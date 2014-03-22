import numpy as np
import Image

__author__ = 'mavinm'
__date__ = '3/21/14'


def rescale_data_to_image(data):
    return (255.0 / data.max() * (data - data.min())).astype(np.uint8)

if __name__ == "__main__":
    filenames = {
        "tmp/bc_data_gaussian_sigma=0.02.bin": "report/bc_gaussian-0.02.png",
        "tmp/bc_data_gaussian_sigma=0.04.bin": "report/bc_gaussian-0.04.png",
        "tmp/bc_data_gaussian_sigma=0.06.bin": "report/bc_gaussian-0.06.png",
        "tmp/bc_data_gaussian_sigma=0.08.bin": "report/bc_gaussian-0.08.png",

        "tmp/bc_data_gaussian_sigma=0.1.bin": "report/bc_gaussian-0.1.png",
        "tmp/bc_data_gaussian_sigma=0.2.bin": "report/bc_gaussian-0.2.png",
        "tmp/bc_data_gaussian_sigma=0.4.bin": "report/bc_gaussian-0.4.png",
        "tmp/bc_data_gaussian_sigma=0.6.bin": "report/bc_gaussian-0.6.png",
        "tmp/bc_data_gaussian_sigma=0.8.bin": "report/bc_gaussian-0.8.png",
        "tmp/bc_data_gaussian_sigma=1.0.bin": "report/bc_gaussian-1.0.png",

        "tmp/gc_data_gaussian_sigma=0.02.bin": "report/gc_gaussian-0.02.png",
        "tmp/gc_data_gaussian_sigma=0.04.bin": "report/gc_gaussian-0.04.png",
        "tmp/gc_data_gaussian_sigma=0.06.bin": "report/gc_gaussian-0.06.png",
        "tmp/gc_data_gaussian_sigma=0.08.bin": "report/gc_gaussian-0.08.png",

        "tmp/gc_data_gaussian_sigma=0.1.bin": "report/gc_gaussian-0.1.png",
        "tmp/gc_data_gaussian_sigma=0.2.bin": "report/gc_gaussian-0.2.png",
        "tmp/gc_data_gaussian_sigma=0.4.bin": "report/gc_gaussian-0.4.png",
        "tmp/gc_data_gaussian_sigma=0.6.bin": "report/gc_gaussian-0.6.png",
        "tmp/gc_data_gaussian_sigma=0.8.bin": "report/gc_gaussian-0.8.png",
        "tmp/gc_data_gaussian_sigma=1.0.bin": "report/gc_gaussian-1.0.png",
    }

    for fn, out in filenames.iteritems():
        data = np.load(fn)
        sigma = fn.split("=")[1].rstrip(".bin")
        print sigma
        rescaled = rescale_data_to_image(data)
        im = Image.fromarray(rescaled)
        im.save(out)