import unittest
import functools
import numpy

from traits.testing.api import UnittestTools
from traits.api import TraitError

from simphony.cuds.particles import Particles, Particle, Bond
from simphony.core.data_container import DataContainer
from simphony.core.cuba import CUBA

from simphony_mayavi.core.api import CUBADataExtractor


class TestCUBADataExtractor(UnittestTools, unittest.TestCase):

    def setUp(self):
        self.points = [
            [0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
        self.temperature = numpy.arange(4)
        self.velocity = [
            (0.5, 0.5, 0.5), (1.0, 0.0, 1.0), (1.0, 1.0, 0.0), (1.0, 1.0, 1.0)]
        self.bonds = [[0, 1], [0, 3], [1, 3, 2]]
        self.container = Particles('test')

        # add particles
        particle_list = []
        for index, point in enumerate(self.points):
            data = DataContainer(
                TEMPERATURE=self.temperature[index],
                VELOCITY=self.velocity[index])
            particle_list.append(Particle(coordinates=point, data=data))
        self.point_uids = self.container.add(particle_list)

        # add bonds
        bond_iter = (Bond(particles=[self.point_uids[index]
                                     for index in indices],
                          data=DataContainer(NAME=str(len(indices))))
                     for indices in self.bonds)
        self.bond_uids = self.container.add(bond_iter)

    def test_initialization(self):
        container = self.container
        extractor = CUBADataExtractor(function=functools.partial(
            container.iter, item_type=CUBA.PARTICLE))
        self.assertEqual(
            extractor.available, set((CUBA.TEMPERATURE, CUBA.VELOCITY)))
        self.assertEqual(extractor.data, {})

    def test_selectinng_available(self):
        container = self.container
        extractor = CUBADataExtractor(function=functools.partial(
            container.iter, item_type=CUBA.PARTICLE))

        with self.assertTraitChanges(extractor, 'data', count=1):
            extractor.selected = CUBA.TEMPERATURE

        self.assertEqual(len(extractor.data), 4)
        for uid, data in extractor.data.iteritems():
            particle = container.get(uid)
            self.assertEqual(particle.data[CUBA.TEMPERATURE], data)

    def test_selecting_none(self):
        extractor = CUBADataExtractor(
            function=functools.partial(
                self.container.iter, item_type=CUBA.PARTICLE))

        with self.assertTraitChanges(extractor, 'data', count=2):
            extractor.selected = CUBA.TEMPERATURE
            extractor.selected = None

        self.assertEqual(extractor.data, {})

    def test_selecting_unavailable(self):
        container = self.container
        extractor = CUBADataExtractor(
            function=functools.partial(container.iter,
                                       item_type=CUBA.PARTICLE))

        with self.assertTraitChanges(extractor, 'data', count=1):
            extractor.selected = CUBA.NAME

        self.assertEqual(len(extractor.data), 4)
        for uid, data in extractor.data.iteritems():
            self.assertTrue(container.has(uid))
            self.assertEqual(data, None)

    def test_function_change(self):
        container = self.container
        extractor = CUBADataExtractor(
            function=functools.partial(container.iter,
                                       item_type=CUBA.PARTICLE))
        extractor.selected = CUBA.TEMPERATURE

        with self.assertRaises(TraitError):
            extractor.function = functools.partial(container.iter,
                                                   item_type=CUBA.BOND)

    def test_keys_filtering(self):
        container = self.container
        extractor = CUBADataExtractor(
            function=functools.partial(
                container.iter,
                item_type=CUBA.PARTICLE),
            keys=set(self.point_uids[:1]))
        extractor.selected = CUBA.TEMPERATURE

        particle = container.get(self.point_uids[0])
        self.assertEqual(
            extractor.data,
            {self.point_uids[0]: particle.data[CUBA.TEMPERATURE]})

    def test_keys_filtering_change(self):
        container = self.container
        extractor = CUBADataExtractor(
            function=functools.partial(
                container.iter,
                item_type=CUBA.PARTICLE), keys=set(self.point_uids[:1]))
        extractor.selected = CUBA.TEMPERATURE

        with self.assertTraitChanges(extractor, 'data', count=1):
            extractor.keys = set(self.point_uids)

        self.assertEqual(len(extractor.data), 4)
        for uid, data in extractor.data.iteritems():
            particle = container.get(uid)
            self.assertEqual(particle.data[CUBA.TEMPERATURE], data)
