import unittest

import numpy

from traits.testing.api import UnittestTools

from simphony.cuds.particles import Particles, Particle, Bond
from simphony.core.data_container import DataContainer
from simphony.core.cuba import CUBA

from simphony_mayavi.sources.cuds_data_extractor import CUDSDataExtractor


class TestCUDSDataExtractor(UnittestTools, unittest.TestCase):

    def setUp(self):
        self.points = [
            [0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
        self.temperature = numpy.arange(4)
        self.velocity = [
            (0.5, 0.5, 0.5), (1.0, 0.0, 1.0), (1.0, 1.0, 0.0), (1.0, 1.0, 1.0)]
        self.bonds = [[0, 1], [0, 3], [1, 3, 2]]
        self.container = Particles('test')
        self.point_uids = []
        for index, point in enumerate(self.points):
            data = DataContainer(
                TEMPERATURE=self.temperature[index],
                VELOCITY=self.velocity[index])
            uid = self.container.add_particle(
                Particle(coordinates=point, data=data))
            self.point_uids.append(uid)

        self.bond_uids = [
            self.container.add_bond(
                Bond(
                    particles=[self.point_uids[index] for index in indices],
                    data=DataContainer(NAME=str(len(indices)))))
            for indices in self.bonds]

    def test_initialization(self):
        container = self.container
        extractor = CUDSDataExtractor(function=container.iter_particles)
        self.assertEqual(
            extractor.available, set((CUBA.TEMPERATURE, CUBA.VELOCITY)))
        self.assertEqual(extractor.data, {})

    def test_selectinng_available(self):
        container = self.container
        extractor = CUDSDataExtractor(function=container.iter_particles)

        with self.assertTraitChanges(extractor, 'data', count=1):
            extractor.selected = CUBA.TEMPERATURE

        for uid, data in extractor.data.iteritems():
            particle = container.get_particle(uid)
            self.assertEqual(particle.data[CUBA.TEMPERATURE], data)

    def test_selecting_none(self):
        extractor = CUDSDataExtractor(function=self.container.iter_particles)

        with self.assertTraitChanges(extractor, 'data', count=2):
            extractor.selected = CUBA.TEMPERATURE
            extractor.selected = None

        self.assertEqual(extractor.data, {})

    def test_selecting_unavailable(self):
        container = self.container
        extractor = CUDSDataExtractor(function=container.iter_particles)

        with self.assertTraitChanges(extractor, 'data', count=1):
            extractor.selected = CUBA.NAME
        for uid, data in extractor.data.iteritems():
            self.assertTrue(container.has_particle(uid))
            self.assertEqual(data, None)

    def test_function_change(self):
        container = self.container
        extractor = CUDSDataExtractor(function=container.iter_particles)
        extractor.selected = CUBA.TEMPERATURE

        with self.assertTraitChanges(extractor, 'data,available'):
            extractor.function = container.iter_bonds

        for uid, data in extractor.data.iteritems():
            self.assertTrue(container.has_bond(uid))
            self.assertEqual(data, None)
