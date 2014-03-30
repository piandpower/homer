import numpy as np
from .opencl import *
from . import image, rotate, staffsize, staves

PAGE_SIZE = 4096

class Page:
    def __init__(self, image_data):
        img = image.image_array(image_data)
        padded_img = np.zeros((PAGE_SIZE, PAGE_SIZE), np.uint8)
        padded_img[:img.shape[0], :img.shape[1]] = img
        self.bitarray = np.packbits(padded_img).reshape((PAGE_SIZE, -1))
        self.img = cla.to_device(q, self.bitarray)

    def process(self):
        logging.info("rotate by %f", rotate.rotate(self))
        logging.info("staffsize %s", str(staffsize.staffsize(self)))
        logging.info("detected %d staves", len(staves.staves(self)))

    def show(self):
        import pylab as p
        p.figure()
        p.imshow(np.unpackbits(self.img.get()).reshape((PAGE_SIZE, PAGE_SIZE)))
        staves.show_staff_centers(self)
