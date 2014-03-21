import numpy as np
import Image

__author__ = 'mavinm'
__date__ = '3/21/14'


def rescale_data_to_image(data):
    return (255.0 / data.max() * (data - data.min())).astype(np.uint8)

if __name__ == "__main__":
    bc_f = "tmp/bc_data_gaussian.bin"
    gc_f = "tmp/gc_data_gaussian.bin"

    bc_data = np.load(bc_f)
    gc_data = np.load(gc_f)
    rescaled_bc = rescale_data_to_image(bc_data)
    rescaled_gc = rescale_data_to_image(gc_data)
    im_bc = Image.fromarray(rescaled_bc)
    im_gc = Image.fromarray(rescaled_gc)
    im_bc.show()
    im_gc.show()