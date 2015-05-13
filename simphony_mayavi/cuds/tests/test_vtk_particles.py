import unittest
import uuid
from functools import partial

from simphony.cuds.particles import Particle, Bond
from simphony.core.data_container import DataContainer
from simphony.core.cuba import CUBA
from simphony.testing.utils import compare_data_containers
from simphony.testing.abc_check_particles import (
    ContainerManipulatingBondsCheck, ContainerAddParticlesCheck,
    ContainerAddBondsCheck, ContainerManipulatingParticlesCheck)
from simphony_mayavi.cuds.api import VTKParticles
from simphony_mayavi.core.api import supported_cuba


class TestVTKParticlesParticleOperations(
        ContainerAddParticlesCheck, unittest.TestCase):

    def supported_cuba(self):
        return supported_cuba()

    def container_factory(self, name):
        return VTKParticles(name=name)

class TestVTKParticlesManipulatingParticles(
        ContainerManipulatingParticlesCheck, unittest.TestCase):

    def supported_cuba(self):
        return supported_cuba()

    def container_factory(self, name):
        return VTKParticles(name=name)


class TestVTKParticlesAddBonds(
        ContainerAddBondsCheck, unittest.TestCase):

    def container_factory(self, name):
        return VTKParticles(name=name)

    def supported_cuba(self):
        return supported_cuba()


class TestVTKParticlesManipulatingBonds(
        ContainerManipulatingBondsCheck, unittest.TestCase):

    def container_factory(self, name):
        return VTKParticles(name=name)

    def supported_cuba(self):
        return supported_cuba()


class TestParticlesDataContainer(unittest.TestCase):

    def setUp(self):
        self.addTypeEqualityFunc(
            DataContainer, partial(compare_data_containers, testcase=self))

    def test_data(self):
        container = VTKParticles(name='foo')
        data = container.data
        data[CUBA.MASS] = 9
        container.data = data
        ret_data = container.data
        self.assertEqual(data, ret_data)
        self.assertIsNot(data, ret_data)
        cur_data = container.data
        cur_data[CUBA.MASS] = 10
        ret_data = container.data
        self.assertEqual(data, ret_data)
        self.assertIsNot(data, ret_data)


if __name__ == '__main__':
    unittest.main()
