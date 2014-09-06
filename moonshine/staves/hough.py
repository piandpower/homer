from ..gpu import *
from .. import filter, hough, bitimage
from ..cl_util import max_kernel
from ..staves import BaseStaves
import numpy as np

class FilteredHoughStaves(BaseStaves):
    def staff_center_lines(self, page):
        staff_filt = filter.staff_center(page)
        page.staff_filt = staff_filt
        thetas = np.linspace(-np.pi/500, np.pi/500, 51)
        rhores = page.staff_thick*3
        page.staff_bins = hough.hough_line_kernel(staff_filt, rhores=rhores,
                              numrho=page.img.shape[0] // rhores, thetas=thetas)
        # Some staves may have multiple Hough peaks so we need to take many more
        # peaks than the number of staves. Also, the strongest Hough response
        # doesn't always correspond to the longest segment, so we need many
        # peaks to find the longest segment, corresponding to the complete
        # staff. Most images shouldn't need this many peaks, but performance
        # doesn't seem to be an issue.
        peaks = hough.houghpeaks(page.staff_bins,
                                 thresh=max_kernel(page.staff_bins)/4.0)
        page.staff_peak_theta = thetas[peaks[:, 0]]
        page.staff_peak_rho = peaks[:, 1]
        lines = hough.hough_lineseg_kernel(staff_filt,
                                     page.staff_peak_rho, page.staff_peak_theta,
                                     rhores=rhores, max_gap=page.staff_dist*8).get()
        page.staff_center_lines = lines
        return lines

    def find_staves(self):
        lines = self.staff_center_lines(self.page)
        staves = hough.hough_paths(lines)
        # Filter out staves which are too short
        good_staves = (staves[:,-1,0] - staves[:,0,0]) > self.page.orig_size[1] / 2.0
        self.staves = staves[good_staves].astype(np.int32)
        return self.staves

    def show_staff_filter(self):
        import pylab as p
        # Overlay staff line points
        staff_filt = np.unpackbits(self.page.staff_filt.get()).reshape((4096, -1))
        staff_line_mask = np.ma.masked_where(staff_filt == 0, staff_filt)
        p.imshow(staff_line_mask, cmap='Greens')
    def show_staff_segments(self):
        self.show_staff_filter()
        import pylab as p
        for x0, x1, y0, y1 in self.page.staff_center_lines:
            p.plot([x0, x1], [y0, y1], 'g')
