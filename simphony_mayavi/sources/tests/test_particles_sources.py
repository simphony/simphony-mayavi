import unittest

import numpy
from numpy.testing import assert_array_equal

from simphony.core.cuba import CUBA
from simphony.cuds.particles import Particles, Particle, Bond
from simphony.core.data_container import DataContainer

from simphony_mayavi.sources.api import ParticlesSource, cell_array_slicer


class TestParticlesSource(unittest.TestCase):

    def setUp(self):
        self.points = [
            [0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
        self.bonds = [[0, 1], [0, 3], [1, 3, 2]]
        self.point_temperature = [10., 20., 30., 40.]
        self.bond_temperature = [60., 80., 190., 5.]

        self.container = Particles('test')
        self.point_uids = [
            self.container.add_particle(
                Particle(
                    coordinates=point,
                    data=DataContainer(
                        TEMPERATURE=self.point_temperature[index])))
            for index, point in enumerate(self.points)]
        self.bond_uids = [
            self.container.add_bond(
                Bond(
                    particles=[self.point_uids[index] for index in indices],
                    data=DataContainer(
                        TEMPERATURE=self.bond_temperature[index])))
            for index, indices in enumerate(self.bonds)]

    def test_particles(self):
        container = self.container
        source = ParticlesSource.from_particles(container)
        points = source.data.points.to_array()

        number_of_particles = len(self.points)
        self.assertEqual(len(points), number_of_particles)
        self.assertEqual(len(source.point2index), number_of_particles)

        self.assertEqual(source.data.point_data.number_of_arrays, 1)
        temperature = source.data.point_data.get_array('TEMPERATURE')
        for key, index in source.point2index.iteritems():
            point = container.get_particle(key)
            assert_array_equal(points[index], point.coordinates)
            self.assertEqual(temperature[index], point.data[CUBA.TEMPERATURE])

    def test_bonds(self):
        container = self.container
        source = ParticlesSource.from_particles(container)
        vtk_source = source.data
        bonds = [
            bond for bond in cell_array_slicer(vtk_source.lines.to_array())]
        number_of_bonds = len(self.bonds)
        self.assertEqual(len(bonds), number_of_bonds)
        self.assertEqual(len(source.bond2index), number_of_bonds)

        self.assertEqual(source.data.cell_data.number_of_arrays, 1)
        temperature = source.data.cell_data.get_array('TEMPERATURE')
        for key, index in source.bond2index.iteritems():
            bond = container.get_bond(key)
            particles = [source.point2index[uid] for uid in bond.particles]
            self.assertEqual(bonds[index], particles)
            self.assertEqual(temperature[index], bond.data[CUBA.TEMPERATURE])

    def test_cell_array_slicer(self):
        data = numpy.array([2, 0, 1, 2, 0, 3, 3, 1, 3, 2])
        slices = [slice for slice in cell_array_slicer(data)]
        assert_array_equal(slices, [[0, 1], [0, 3], [1, 3, 2]])
