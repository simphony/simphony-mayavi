import unittest
from functools import partial
import random
import uuid

from tvtk.api import tvtk
from simphony.cuds.particles import Particle, Bond, Particles
from simphony.core.data_container import DataContainer
from simphony.core.cuba import CUBA
from simphony.testing.utils import (
    compare_data_containers, compare_particles, compare_bonds,
    create_bonds_with_id, create_bonds, create_particles_with_id,
    create_data_container)
from simphony.testing.abc_check_particles import (
    CheckParticlesContainer,
    CheckAddingParticles, CheckManipulatingParticles,
    CheckAddingBonds, CheckManipulatingBonds)

from simphony_mayavi.cuds.api import VTKParticles
from simphony_mayavi.core.api import (
    supported_cuba, VTKEDGETYPES, VTKFACETYPES)


class TestVTKParticlesAddingParticlesOperations(
        CheckAddingParticles, unittest.TestCase):

    def supported_cuba(self):
        return supported_cuba()

    def container_factory(self, name):
        return VTKParticles(name=name)


class TestVTKParticlesManipulatingParticles(
        CheckManipulatingParticles, unittest.TestCase):

    def supported_cuba(self):
        return supported_cuba()

    def container_factory(self, name):
        return VTKParticles(name=name)


class TestVTKParticlesAddingBonds(
        CheckAddingBonds, unittest.TestCase):

    def container_factory(self, name):
        return VTKParticles(name=name)

    def supported_cuba(self):
        return supported_cuba()

    def test_add_multiple_bonds_with_id(self):
        # for simphony-common 0.2.1 when Bond can be added
        # even if it contains particles that are not part of
        # the container (proposed to throw ValueError, see wiki)

        # given
        container = self.container
        bonds = create_bonds_with_id(particles=self.particle_list,
                                     restrict=supported_cuba())

        # when
        uids = container.add_bonds(bonds)

        # then
        for bond in bonds:
            uid = bond.uid
            self.assertIn(uid, uids)
            self.assertTrue(container.has_bond(uid))
            self.assertEqual(container.get_bond(uid), bond)

    def test_add_multiple_bonds_with_unsupported_cuba(self):
        # for simphony-common 0.2.1 when Bond can be added
        # even if it contains particles that are not part of
        # the container (proposed to throw ValueError, see wiki)

        # given
        container = self.container
        bonds = []
        particle_ids = [particle.uid for particle in self.particle_list]
        for i in xrange(5):
            data = create_data_container()
            ids = random.sample(particle_ids, 5)
            bonds.append(Bond(particles=ids, data=data))

        # when
        container.add_bonds(bonds)

        # then
        for bond in bonds:
            bond.data = create_data_container(
                restrict=self.supported_cuba())
            uid = bond.uid
            self.assertTrue(container.has_bond(uid))
            self.assertEqual(container.get_bond(uid), bond)

    def test_exception_when_adding_multiple_invalid_bonds(self):
        # new test for adding bonds with particles that are
        # not part of the container
        # (proposed to throw ValueError, see wiki)

        # given
        container = self.container
        bonds = create_bonds_with_id()

        with self.assertRaises(ValueError):
            container.add_bonds(bonds)


class TestVTKParticlesManipulatingBonds(
        CheckManipulatingBonds, unittest.TestCase):

    def container_factory(self, name):
        return VTKParticles(name=name)

    def supported_cuba(self):
        return supported_cuba()

    def test_update_multiple_bonds(self):
        # for simphony-common 0.2.1 when Bond can be added
        # even if it contains particles that are not part of
        # the container (proposed to throw ValueError, see wiki)

        # given
        container = self.container
        bonds = self.bond_list
        particle_uids = [particle.uid for particle in self.particle_list]
        for bond in bonds:
            bond.particles = tuple(random.sample(particle_uids, 3))

        # update_bonds not yet called
        for uid, bond in map(None, self.ids, bonds):
            retrieved = container.get_bond(uid)
            self.assertNotEqual(retrieved, bond)

        # when
        container.update_bonds(bonds)
        # then
        for uid, bond in map(None, self.ids, bonds):
            retrieved = container.get_bond(uid)
            self.assertEqual(retrieved, bond)

    def test_exception_when_updating_mulitple_invalid_bond(self):
        # new test for adding bonds with particles that are
        # not part of the container
        # (proposed to throw ValueError, see wiki)

        # given
        container = self.container
        bonds = self.bond_list
        new_ids = [uuid.uuid4() for x in xrange(10)]
        for bond in bonds:
            bond.particles = random.sample(new_ids, 5)

        with self.assertRaises(ValueError):
            container.update_bonds(bonds)

    def test_exception_when_updating_invalid_bond(self):
        # new test for adding bonds with particles that are
        # not part of the container
        # (proposed to throw ValueError, see wiki)

        # given
        container = self.container
        new_ids = [uuid.uuid4() for x in xrange(5)]

        # when
        bond = container.get_bond(self.ids[1])
        bond.particles = new_ids

        with self.assertRaises(ValueError):
            container.update_bonds([bond])


class TestVTKParticlesContainer(CheckParticlesContainer, unittest.TestCase):

    def container_factory(self, name):
        return VTKParticles(name=name)

    def supported_cuba(self):
        return set(CUBA)


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
        uid = container.add_particles((particle,))[0]
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
        point_uids = reference.add_particles((
                Particle(
                    coordinates=point,
                    data=DataContainer(
                        TEMPERATURE=point_temperature[index]))
                for index, point in enumerate(points)))
        bond_uids = reference.add_bonds((
                Bond(
                    particles=[point_uids[index] for index in indices],
                    data=DataContainer(
                        TEMPERATURE=bond_temperature[index]))
                for index, indices in enumerate(bonds)))

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
