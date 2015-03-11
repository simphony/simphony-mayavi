import unittest

import numpy
from numpy.testing import assert_array_equal

from simphony.cuds.lattice import (
    Lattice, make_hexagonal_lattice, make_square_lattice,
    make_cubic_lattice, make_rectangular_lattice, make_orthorombicp_lattice)
from simphony_mayavi.sources.api import LatticeSource


class TestLatticeSource(unittest.TestCase):

    def test_source_from_a_square_lattice(self):
        lattice = make_square_lattice(
            'test', 0.2, (12, 22), origin=(0.2, -2.4))
        source = LatticeSource.from_lattice(lattice)
        data = source.data
        self.assertEqual(data.number_of_points, 12 * 22)
        assert_array_equal(data.origin, (0.2, -2.4, 0.0))

    def test_source_from_a_rectangular_lattice(self):
        lattice = make_rectangular_lattice(
            'test', (0.3, 0.35), (13, 23), origin=(0.2, -2.7))
        source = LatticeSource.from_lattice(lattice)
        data = source.data
        self.assertEqual(data.number_of_points, 13 * 23)
        assert_array_equal(data.origin, (0.2, -2.7, 0.0))

    def test_source_from_a_cubic_lattice(self):
        lattice = make_cubic_lattice('test', 0.4, (14, 24, 34), (4, 5, 6))
        source = LatticeSource.from_lattice(lattice)
        data = source.data
        self.assertEqual(data.number_of_points, 14 * 24 * 34)
        assert_array_equal(data.origin, (4.0, 5.0, 6.0))

    def test_source_from_an_orthorombic_p_lattice(self):
        lattice = make_orthorombicp_lattice(
            'test',  (0.5, 0.54, 0.58), (15, 25, 35), (7, 9, 8))
        source = LatticeSource.from_lattice(lattice)
        data = source.data
        self.assertEqual(data.number_of_points, 15 * 25 * 35)
        assert_array_equal(data.origin, (7.0, 9.0, 8.0))

    def test_source_from_a_hexagonal_lattice(self):
        lattice = make_hexagonal_lattice('test', 0.1, (5, 4))
        source = LatticeSource.from_lattice(lattice)
        data = source.data
        self.assertEqual(data.number_of_points, 5 * 4)
        xspace, yspace = lattice.base_vect
        for index, point in enumerate(data.points):
            # The lattice has 4 rows (y axis) and 5 columns (x axis).
            # Thus the correct size to unravel is (4, 5) instead of
            # (5, 4).
            row, column = numpy.unravel_index(index,  (4, 5))
            assert_array_equal(
                point, (
                    xspace * column + 0.5 * xspace * (row % 2),
                    yspace * row,
                    0.0))

    def test_source_from_unknown(self):
        lattice = Lattice('test', '', (1, 1, 1), (1, 1, 1), (0, 0, 0))
        with self.assertRaises(ValueError):
            LatticeSource.from_lattice(lattice)
