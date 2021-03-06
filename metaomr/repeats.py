# For each staff, look for dots in the correct position before or after
# each barline.

from . import bitimage, components
from .gpu import *
import numpy as np

def staff_dots(page, staff_num):
    sd = page.staves.staff_dist[staff_num]
    img = page.staves.extract_staff(staff_num, img=page.staves.nostaff())
    img = bitimage.erode(img, page.staff_thick)
    img = bitimage.as_hostimage(img)
    # Need a byte per pixel for components
    byteimg = thr.to_device(img)
    # classes are all 1
    classes, bounds, num_pixels = components.get_components(byteimg)
    bounds = bounds.get()
    num_pixels = num_pixels.get()
    width = bounds[:, 1] - bounds[:, 0] + 1
    height = bounds[:, 3] - bounds[:, 2] + 1
    repeat_dot_size = ((width <= sd / 3) & (height <= sd / 3))
    potential_dots = bounds[repeat_dot_size]
    return potential_dots

def staff_repeats(page, staff_num):
    dots = staff_dots(page, staff_num).reshape((-1, 2, 2)).mean(axis=-1)
    sd = page.staves.staff_dist[staff_num]
    is_y = np.min(np.abs(dots[:,1,None] - [[sd*1.5, sd*2.5]]), axis=1) < sd/2
    repeats = []
    for barline in page.barlines[staff_num]:
        result = ''
        if barline[1] - barline[0] >= page.staff_thick*2:
            for x, label in ((barline[0] - sd/2, 'L'), (barline[1] + sd/2, 'R')):
                if (is_y & (np.abs(dots[:,0] - x) < sd/3)).sum() == 2:
                    result += label
        repeats.append(result)
    return repeats

def get_repeats(page):
    page.repeats = [staff_repeats(page, staff_num)
                    for staff_num in xrange(len(page.staves()))]
    return page.repeats
