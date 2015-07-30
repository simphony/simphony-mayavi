import unittest
from functools import partial

from tvtk.api import tvtk
from simphony.cuds.particles import Particle, Bond, Particles
from simphony.core.data_container import DataContainer
from simphony.core.cuba import CUBA
from simphony.testing.utils import (
    compare_data_containers, compare_particles, compare_bonds)
from simphony.testing.abc_check_particles import (
    ContainerManipulatingBondsCheck, ContainerAddParticlesCheck,
    ContainerAddBondsCheck, ContainerManipulatingParticlesCheck)

from simphony_mayavi.cuds.api import VTKParticles
from simphony_mayavi.core.api import (
    supported_cuba, VTKEDGETYPES, VTKFACETYPES)


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


class TestVTKParticlesDataContainer(unittest.TestCase):

    def setUp(self):
        self.addTypeEqualityFunc(
            DataContainer, partial(compare_data_containers, testcase=self))
        self.addTypeEqualityFunc(
            Particle, partial(compare_particles, testcase=self))
        self.addTypeEqualityFunc(
            Bond, partial(compare_bonds, testcase=self))

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

    def test_initialization_with_expected_size(self):
        data_set = tvtk.PolyData(points=tvtk.Points(), lines=[])
        container = VTKParticles(name='test', data_set=data_set)
        particle = Particle(coordinates=(0.0, 1.0, 2.0), data=DataContainer())
        uid = container.add_particle(particle)
        self.assertTrue(container.has_particle(uid))
        self.assertEqual(list(container.iter_bonds()), [])
        self.assertEqual(len(tuple(container.iter_particles())), 1)
        self.assertEqual(container.get_particle(uid), particle)

    def test_initialization_with_cuds(self):
        # given
        points = [
            [0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
        bonds = [[0, 1], [0, 3], [1, 3, 2]]
        point_temperature = [10., 20., 30., 40.]
        bond_temperature = [60., 80., 190., 5.]
        reference = Particles('test')
        point_uids = [
            reference.add_particle(
                Particle(
                    coordinates=point,
                    data=DataContainer(
                        TEMPERATURE=point_temperature[index])))
            for index, point in enumerate(points)]
        bond_uids = [
            reference.add_bond(
                Bond(
                    particles=[point_uids[index] for index in indices],
                    data=DataContainer(
                        TEMPERATURE=bond_temperature[index])))
            for index, indices in enumerate(bonds)]

        # when
        container = VTKParticles.from_particles(reference)

        # then
        number_of_particles = sum(1 for _ in container.iter_particles())
        self.assertEqual(number_of_particles, len(point_uids))
        for expected in reference.iter_particles():
            self.assertEqual(container.get_particle(expected.uid), expected)
        number_of_bonds = sum(1 for _ in container.iter_bonds())
        self.assertEqual(number_of_bonds, len(bond_uids))
        for expected in reference.iter_bonds():
            self.assertEqual(container.get_bond(expected.uid), expected)

    def test_initialization_with_empty_cuds(self):
        # given
        reference = Particles('test')

        # when
        container = VTKParticles.from_particles(reference)

        # then
        number_of_particles = sum(1 for _ in container.iter_particles())
        self.assertEqual(number_of_particles, 0)
        number_of_bonds = sum(1 for _ in container.iter_bonds())
        self.assertEqual(number_of_bonds, 0)

    def test_initialization_with_poly_data(self):
        # given
        bonds = [
            [0, 1, 2, 3],
            [4, 5, 6, 7, 8, 9, 10, 11],
            [2, 7, 11],
            [1, 4],
            [1, 5, 8]]
        points = [(i, i*2, i*3) for i in range(12)]
        vtk = tvtk.PolyData(points=points, lines=bonds)

        # when
        container = VTKParticles.from_dataset(name='test', data_set=vtk)

        # then
        number_of_particles = sum(1 for _ in container.iter_particles())
        self.assertEqual(number_of_particles, 12)
        for particle in container.iter_particles():
            self.assertIsNotNone(particle.uid)
        number_of_bonds = sum(1 for _ in container.iter_bonds())
        self.assertEqual(number_of_bonds, 5)
        uids = [particle.uid for particle in container.iter_particles()]
        for bond in container.iter_bonds():
            self.assertIsNotNone(bond.uid)
            self.assertTrue(set(bond.particles).issubset(uids))

    def test_initialization_with_unstructured_grid(self):
        # given
        bonds = [
            [0, 1, 2, 3],
            [4, 5, 6, 7, 8, 9, 10, 11],
            [2, 7, 11],
            [1, 4],
            [1, 5, 8]]
        points = [(i, i*2, i*3) for i in range(12)]
        vtk = tvtk.UnstructuredGrid(points=points)
        for bond in bonds:
            if len(bond) > 2:
                vtk.insert_next_cell(VTKEDGETYPES[1], bond)
            else:
                vtk.insert_next_cell(VTKEDGETYPES[0], bond)

        # when
        container = VTKParticles.from_dataset(name='test', data_set=vtk)

        # then
        number_of_particles = sum(1 for _ in container.iter_particles())
        self.assertEqual(number_of_particles, 12)
        for particle in container.iter_particles():
            self.assertIsNotNone(particle.uid)
        number_of_bonds = sum(1 for _ in container.iter_bonds())
        self.assertEqual(number_of_bonds, 5)
        uids = [particle.uid for particle in container.iter_particles()]
        for bond in container.iter_bonds():
            self.assertIsNotNone(bond.uid)
            self.assertTrue(set(bond.particles).issubset(uids))

    def test_initialization_with_invalid_unstructured_grid(self):
        # given
        bonds = [
            [0, 1, 2, 3],
            [4, 5, 6, 7, 8, 9, 10, 11],
            [2, 7, 11],
            [1, 4],
            [1, 5, 8]]
        points = [(i, i*2, i*3) for i in range(12)]
        vtk = tvtk.UnstructuredGrid(points=points)
        for bond in bonds:
            if len(bond) > 2:
                vtk.insert_next_cell(VTKEDGETYPES[1], bond)
            else:
                vtk.insert_next_cell(VTKEDGETYPES[0], bond)
        vtk.insert_next_cell(VTKFACETYPES[0], [0, 1, 2])

        # when/then
        with self.assertRaises(TypeError):
            VTKParticles.from_dataset(name='test', data_set=vtk)

    def test_initialization_with_image_data(self):
        # given
        vtk = tvtk.ImageData()
        vtk.extent = 0, 4, 0, 2, 0, 14

        # when/then
        with self.assertRaises(TypeError):
            VTKParticles.from_dataset(name='test', data_set=vtk)


if __name__ == '__main__':
    unittest.main()
