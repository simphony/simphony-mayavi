import unittest
from functools import partial

import numpy
from numpy.testing import assert_array_equal

from simphony.core.cuba import CUBA
from simphony.testing.abc_check_lattice import (
    CheckLatticeNodeOperations, CheckLatticeNodeCoordinates,
    CheckLatticeProperties)
from simphony.testing.utils import compare_lattice_nodes
from simphony.core.data_container import DataContainer
from simphony.cuds.lattice import make_hexagonal_lattice, LatticeNode

from simphony_mayavi.cuds.api import VTKLattice
from simphony_mayavi.core.api import supported_cuba
from simphony_mayavi.sources.api import LatticeSource


class TestVTKLatticeNodeOperations(
        CheckLatticeNodeOperations, unittest.TestCase):

    def container_factory(self, name, type_, base_vect, size, origin):
        return VTKLattice.empty(name, type_, base_vect, size, origin)

    def supported_cuba(self):
        return supported_cuba()


class TestVTKLatticeProperties(
        CheckLatticeProperties, unittest.TestCase):

    def container_factory(self, name, type_, base_vect, size, origin):
        return VTKLattice.empty(name, type_, base_vect, size, origin)

    def supported_cuba(self):
        return set(CUBA)


class TestVTKLatticeNodeCoordinates(
        CheckLatticeNodeCoordinates, unittest.TestCase):

    def container_factory(self, name, type_, base_vect, size, origin):
        return VTKLattice.empty(name, type_, base_vect, size, origin)

    def supported_cuba(self):
        return supported_cuba()


class TestVTKLattice(unittest.TestCase):

    def setUp(self):
        self.addTypeEqualityFunc(
            LatticeNode, partial(compare_lattice_nodes, testcase=self))

    def test_creating_a_xy_plane_hexagonal_lattice(self):
        # given
        lattice = make_hexagonal_lattice('test', 0.1, (5, 4))
        self.add_velocity(lattice)
        source = LatticeSource.from_lattice(lattice)
        data = source.data

        # when
        vtk_lattice = VTKLattice(
            name=lattice.name,
            type_=lattice.type,
            data_set=data)

        # then
        xspace, yspace, _ = lattice.base_vect
        self.assertEqual(vtk_lattice.size, lattice.size)
        assert_array_equal(vtk_lattice.origin, lattice.origin)
        assert_array_equal(vtk_lattice.base_vect, lattice.base_vect)

    def test_get_node_on_a_xy_plane_hexagonal_lattice(self):
        # given
        lattice = make_hexagonal_lattice('test', 0.1, (5, 4))
        self.add_velocity(lattice)
        source = LatticeSource.from_lattice(lattice)
        data = source.data
        vtk_lattice = VTKLattice(
            name=lattice.name,
            type_=lattice.type,
            data_set=data)

        # when
        node = vtk_lattice.get_node((1, 1, 0))

        # then
        self.assertEqual(
            node, LatticeNode(
                (1, 1, 0),
                data=DataContainer(VELOCITY=(1, 1, 0))))

    def test_iter_nodes_on_a_xy_plane_hexagonal_lattice(self):
        # given
        lattice = make_hexagonal_lattice('test', 0.1, (5, 4))
        self.add_velocity(lattice)
        source = LatticeSource.from_lattice(lattice)
        data = source.data
        vtk_lattice = VTKLattice(
            name=lattice.name,
            type_=lattice.type,
            data_set=data)

        # when/then
        for node in vtk_lattice.iter_nodes():
            self.assertEqual(
                node, LatticeNode(
                    node.index,
                    data=DataContainer(VELOCITY=node.index)))
        self.assertEqual(sum(1 for _ in vtk_lattice.iter_nodes()), 20)

    def test_update_nodes_on_a_xy_plane_hexagonal_lattice(self):
        # given
        lattice = make_hexagonal_lattice('test', 0.1, (5, 4))
        self.add_velocity(lattice)
        source = LatticeSource.from_lattice(lattice)
        data = source.data
        vtk_lattice = VTKLattice(
            name=lattice.name,
            type_=lattice.type,
            data_set=data)
        node = vtk_lattice.get_node((1, 1, 0))

        # when
        node.data = DataContainer(VELOCITY=(1, 54, 0.3))
        vtk_lattice.update_node(node)

        # then
        new_node = vtk_lattice.get_node((1, 1, 0))
        self.assertEqual(
            new_node, LatticeNode(
                (1, 1, 0),
                data=DataContainer(VELOCITY=(1, 54, 0.3))))

    def test_get_coordinate_on_a_xy_plane_hexagonal_lattice(self):
        # given
        lattice = make_hexagonal_lattice('test', 0.1, (5, 4))
        self.add_velocity(lattice)
        source = LatticeSource.from_lattice(lattice)
        data = source.data
        vtk_lattice = VTKLattice(
            name=lattice.name,
            type_=lattice.type,
            data_set=data)

        # when/then
        for point_id, point in enumerate(data.points):
            index = numpy.unravel_index(point_id, vtk_lattice.size, order='F')
            assert_array_equal(vtk_lattice.get_coordinate(index), point)

    def add_velocity(self, lattice):
        for node in lattice.iter_nodes():
            node.data[CUBA.VELOCITY] = node.index
            lattice.update_node(node)


if __name__ == '__main__':
    unittest.main()
