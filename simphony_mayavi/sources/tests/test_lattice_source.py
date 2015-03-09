import unittest

from simphony.cuds.lattice import (
    Lattice, LatticeNode, make_hexagonal_lattice, make_square_lattice,
    make_cubic_lattice, make_rectangular_lattice, make_orthorombicp_lattice)
from simphony_mayavi.sources import LatticeSource


class TestParticlesSource(unittest.TestCase):

    def test_source_from_a_square_lattice(self):
        lattice = make_square_lattice(
            'test', 0.2, (12, 22), origin=(0.2, -2.4))
        source = LatticeSource.from_lattice(lattice)
        data = source.data
        self.assertEqual(data.number_of_points, 12 * 22)

    def test_source_from_a_rectangular_lattice(self):
        lattice = make_rectangular_lattice(
            'test', (0.3, 0.35), (13, 23), origin=(0.2, -2.4))
        source = LatticeSource.from_lattice(lattice)
        data = source.data
        self.assertEqual(data.number_of_points, 13 * 23)

    def test_source_from_a_cubic_lattice(self):
        lattice = make_cubic_lattice('test', 0.4, (14, 24, 34), (4, 5, 6))
        source = LatticeSource.from_lattice(lattice)
        data = source.data
        self.assertEqual(data.number_of_points, 14 * 24 * 34)

    def test_source_from_a_cubic_lattice(self):
        lattice = make_cubic_lattice('test', 0.4, (14, 24, 34), (4, 5, 6))
        source = LatticeSource.from_lattice(lattice)
        data = source.data
        self.assertEqual(data.number_of_points, 14 * 24 * 34)

    def test_source_from_a_orthotombicp_lattice(self):
        lattice = make_orthorombicp_lattice(
            'test',  (0.5, 0.54, 0.58), (15, 25, 35), (7, 8, 9))
        source = LatticeSource.from_lattice(lattice)
        data = source.data
        self.assertEqual(data.number_of_points, 15 * 25 * 35)

    def test_source_from_a_hexagonal_lattice(self):
        lattice = make_hexagonal_lattice('test', 0.1, (11, 21))
        source = LatticeSource.from_lattice(lattice)
        data = source.data
        self.assertEqual(data.number_of_points, 11 * 21)

    def test_source_from_unknown(self):
        lattice = Lattice('test', '', (1, 1, 1), (1, 1, 1), (0, 0, 0))
        with self.assertRaises(ValueError):
            LatticeSource.from_lattice(lattice)
