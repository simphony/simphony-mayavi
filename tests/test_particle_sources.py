import unittest

import numpy
from numpy.testing import assert_array_equal

from simphony.cuds.particles import ParticleContainer, Particle, Bond
from simphony_mayavi.sources import ParticleSource, cell_array_slicer


class TestParticleSource(unittest.TestCase):

    def setUp(self):
        self.points = [
            [0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
        self.bonds = [[0, 1], [0, 3], [1, 3, 2]]
        self.container = ParticleContainer('test')
        self.point_uids = [
            self.container.add_particle(Particle(coordinates=point))
            for point in self.points]
        self.bond_uids = [
            self.container.add_bond(
                Bond(particles=[self.point_uids[index] for index in indices]))
            for indices in self.bonds]

    def test_particles(self):
        container = self.container
        source = ParticleSource.from_particles(container)
        points = source.data.points.to_array()

        number_of_particles = len(self.points)
        self.assertEqual(len(points), number_of_particles)
        self.assertEqual(len(source.point2index), number_of_particles)

        for key, index in source.point2index.iteritems():
            point = container.get_particle(key)
            assert_array_equal(points[index], point.coordinates)

    def test_bonds(self):
        container = self.container
        source = ParticleSource.from_particles(container)
        vtk_source = source.data
        bonds = [
            bond for bond in cell_array_slicer(vtk_source.lines.to_array())]
        number_of_bonds = len(self.bonds)
        self.assertEqual(len(bonds), number_of_bonds)
        self.assertEqual(len(source.bond2index), number_of_bonds)

        for key, index in source.bond2index.iteritems():
            bond = container.get_bond(key)
            particles = [source.point2index[uid] for uid in bond.particles]
            self.assertEqual(bonds[index], particles)

    def test_cell_array_slicer(self):
        data = numpy.array([2, 0, 1, 2, 0, 3, 3, 1, 3, 2])
        slices = [slice for slice in cell_array_slicer(data)]
        assert_array_equal(slices, [[0, 1], [0, 3], [1, 3, 2]])

    def test_particle_data_properties(self):
