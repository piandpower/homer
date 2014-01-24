from .pagetree import PageTree
from . import staff, staffsystem
from numpy import *

class Layout:
  def __init__(self, page):
    self.page = page

  def build_staves(self):
    self.tree = self.page.tree = PageTree(self.page)
    self.page.staff_builder = staff.StaffBuilder(self.page)
    self.page.staff_builder.process()

  def segment_staves(self):
    self.page.staff_segmenter = staff.StaffSegmenter(self.page)
    self.page.staff_segmenter.process()

  def build_staff_systems(self):
    self.page.system_builder = staffsystem.SystemBuilder(self.page)
    self.page.system_builder.process()

  def process(self):
    self.build_staves()
    self.segment_staves()
    self.build_staff_systems()

  def show(self, show_grid=True, show_boundaries=True, show_measures=True):
    if show_grid:
      self.page.staff_builder.show()

    if show_boundaries:
      self.page.staff_segmenter.show()

    if show_measures:
      self.page.system_builder.show()