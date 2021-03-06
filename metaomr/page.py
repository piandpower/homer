import numpy as np
from .gpu import *
from . import image, bitimage, settings
from . import staffsize, orientation, staves
from . import barlines, repeats, systems
from . import staffboundary, measure#, note

class Page(object):
    def __init__(self, image_data):
        if hasattr(image_data, 'dtype') and not isinstance(image_data, np.ndarray):
            self.img = image_data
            self.byteimg = bitimage.as_hostimage(self.img)
            self.orig_size = self.byteimg.shape
            self.size = self.img.shape
        else:
            if isinstance(image_data, np.ndarray):
                img = image_data
            else:
                self.image_data = image_data
                img = image.image_array(image_data)

            pad_size, new_size = self.padded_size(img.shape)
            if new_size != img.shape:
                import scipy
                img = scipy.misc.imresize(img, new_size, 'nearest')
                img = img != 0
            padded_img = np.zeros(pad_size, np.uint8)
            padded_img[:img.shape[0], :img.shape[1]] = img
            self.byteimg = padded_img
            self.orig_size = img.shape
            self.img = bitimage.as_bitimage(padded_img)
            self.size = pad_size

        self.rotation = orientation.Rotation(self)
        self.staves = staves.Staves(self)

    def padded_size(self, shape):
        size = max(shape)
        MAXSIZE = settings.IMAGE_MAX_SIZE
        if size > MAXSIZE:
            if shape[0] > shape[1]:
                new_size = (MAXSIZE, shape[1] * MAXSIZE / shape[0])
            else:
                new_size = (shape[0] * MAXSIZE / shape[1], MAXSIZE)
        else:
            new_size = shape
        pad_size = tuple(-(-s & -settings.IMAGE_ALIGNMENT) for s in new_size)
        return pad_size, new_size

    def preprocess(self):
        staffsize.staffsize(self)
        if type(self.staff_dist) is not int:
            return
        self.rotation()
        # If we rotate significantly, the vertical difference between staff
        # lines may be slightly different
        staffsize.staffsize(self)

    def layout(self):
        if not hasattr(self, 'staff_dist'):
            self.preprocess()
        self.staves()
        barlines.get_barlines(self)
        repeats.get_repeats(self)
        systems.build_systems(self)

    def process(self):
        self.preprocess()
        if self.staff_dist is None:
            return False
        else:
            self.layout()
            staffboundary.boundaries(self)
            measure.build_bars(self)
            return True

    def get_notepitch_score(self):
        staffboundary.boundaries(self)
        measure.build_bars(self)
        self.notepitch_score = note.get_notepitch_score(self)
        return self.notepitch_score

    def show(self, show_layout=True, show_elements=False):
        import pylab
        from . import bitimage
        pylab.figure()
        pylab.imshow(bitimage.as_hostimage(self.img))
        pylab.ylim([self.orig_size[0], 0])
        pylab.xlim([0, self.orig_size[1]])
        if show_layout:
            self.staves.show()
            barlines.show_barlines(self)
            systems.show_system_barlines(self)
            #staffboundary.show_boundaries(self)
        if show_elements:
            for barsystem in self.bars:
                for system_measure in barsystem:
                    for part in system_measure:
                        part.show_elements(on_page=True)
