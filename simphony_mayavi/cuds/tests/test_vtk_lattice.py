import unittest

import numpy
from numpy.testing import assert_array_equal

from simphony.core.cuba import CUBA
from simphony.testing.abc_check_lattice import ABCCheckLattice
from simphony.core.data_container import DataContainer
from simphony.cuds.lattice import make_hexagonal_lattice

from simphony_mayavi.cuds.api import VTKLattice
from simphony_mayavi.core.api import supported_cuba
from simphony_mayavi.sources.api import LatticeSource


class TestVTKLattice(ABCCheckLattice, unittest.TestCase):

    def container_factory(self, name, type_, base_vect, size, origin):
        return VTKLattice.empty(name, type_, base_vect, size, origin)

    def supported_cuba(self):
        return supported_cuba()

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
        self.assertEqual(node.index, (1, 1, 0))
        self.assertEqual(node.data, DataContainer(VELOCITY=(1, 1, 0)))

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
            self.assertEqual(node.data, DataContainer(VELOCITY=node.index))
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
        self.assertEqual(new_node.data, DataContainer(VELOCITY=(1, 54, 0.3)))

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

    def test_set_modify_data(self):
        """ Check that data can be retrieved and is consistent. Check that
        the internal data of the lattice cannot be modified outside the
        lattice class
        """
        lattice = self.container_factory('test_lat', 'Cubic',
                                         (1.0, 1.0, 1.0), (4, 3, 2),
                                         (0, 0, 0))
        org_data = DataContainer()

        org_data[CUBA.VELOCITY] = (0, 0, 0)

        lattice.data = org_data
        ret_data = lattice.data

        self.assertEqual(org_data, ret_data)
        self.assertIsNot(org_data, ret_data)

        org_data = DataContainer()

        org_data[CUBA.VELOCITY] = (0, 0, 0)

        lattice.data = org_data
        mod_data = lattice.data

        mod_data[CUBA.VELOCITY] = (1, 1, 1)

        ret_data = lattice.data

        self.assertEqual(org_data, ret_data)
        self.assertIsNot(org_data, ret_data)

    def add_velocity(self, lattice):
        for node in lattice.iter_nodes():
            node.data[CUBA.VELOCITY] = node.index
            lattice.update_node(node)


if __name__ == '__main__':
    unittest.main()
