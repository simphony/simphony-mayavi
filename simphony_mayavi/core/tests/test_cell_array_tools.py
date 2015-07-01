import unittest

import numpy
from numpy.testing import assert_array_equal

from simphony_mayavi.core.api import cell_array_slicer


class TestCellArrayTools(unittest.TestCase):

    def test_cell_array_slicer(self):
        data = numpy.array([2, 0, 1, 2, 0, 3, 3, 1, 3, 2])
        slices = [slice for slice in cell_array_slicer(data)]
        assert_array_equal(slices, [[0, 1], [0, 3], [1, 3, 2]])
