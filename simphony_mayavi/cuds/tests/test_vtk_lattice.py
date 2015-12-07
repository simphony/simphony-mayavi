import unittest
from functools import partial

from numpy.testing import assert_array_equal
from hypothesis import given
from hypothesis.strategies import sampled_from
from tvtk.api import tvtk

from simphony.core.cuba import CUBA
from simphony.testing.abc_check_lattice import (
    CheckLatticeNodeOperations, CheckLatticeNodeCoordinates)
from simphony.testing.utils import compare_lattice_nodes
from simphony.core.data_container import DataContainer
from simphony.cuds.lattice import (
    make_hexagonal_lattice, make_cubic_lattice, make_orthorhombic_lattice,
    make_body_centered_cubic_lattice, make_face_centered_cubic_lattice,
    make_rhombohedral_lattice, make_tetragonal_lattice,
    make_body_centered_tetragonal_lattice,
    make_face_centered_orthorhombic_lattice,
    make_base_centered_orthorhombic_lattice,
    make_body_centered_orthorhombic_lattice,
    make_monoclinic_lattice,
    make_base_centered_monoclinic_lattice,
    make_triclinic_lattice,
    Lattice, LatticeNode)
from simphony.cuds.primitive_cell import BravaisLattice, PrimitiveCell

from simphony_mayavi.cuds.api import VTKLattice
from simphony_mayavi.core.api import supported_cuba


lattice_types = sampled_from([
    make_cubic_lattice('test', 0.1, (3, 6, 5)),
    make_hexagonal_lattice('test', 0.1, 0.2, (5, 4, 6)),
    make_orthorhombic_lattice('test', (0.1, 0.2, 0.3), (3, 7, 6)),
    make_body_centered_cubic_lattice('test', 0.1, (3, 6, 5)),
    make_face_centered_cubic_lattice('test', 0.1, (3, 6, 5)),
    make_rhombohedral_lattice('test', 0.1, 0.2, (3, 6, 5)),
    make_tetragonal_lattice('test', 0.1, 0.2, (3, 6, 5)),
    make_body_centered_tetragonal_lattice('test', 0.1, 0.5, (3, 6, 5)),
    make_face_centered_orthorhombic_lattice('test', (0.5, 0.6, 0.7),
                                            (3, 6, 5)),
    make_base_centered_orthorhombic_lattice('test', (0.5, 0.6, 0.7),
                                            (3, 6, 5)),
    make_body_centered_orthorhombic_lattice('test', (0.5, 0.6, 0.7),
                                            (3, 6, 5)),
    make_monoclinic_lattice('test', (0.5, 0.6, 0.7), 0.4,
                            (3, 6, 5)),
    make_base_centered_monoclinic_lattice('test', (0.5, 0.6, 0.7),
                                          0.4, (3, 6, 5)),
    make_triclinic_lattice('test', (0.5, 0.6, 0.7), (0.4, 0.3, 0.2),
                           (3, 6, 5))])


class TestVTKLatticeNodeOperations(
        CheckLatticeNodeOperations, unittest.TestCase):

    def container_factory(self, name, primitive_cell, size, origin):
        return VTKLattice.empty(name, primitive_cell, size, origin)

    def supported_cuba(self):
        return supported_cuba()


class TestVTKLatticeNodeCoordinates(
        CheckLatticeNodeCoordinates, unittest.TestCase):

    def container_factory(self, name, primitive_cell, size, origin):
        return VTKLattice.empty(name, primitive_cell, size, origin)

    def supported_cuba(self):
        return supported_cuba()


class TestVTKLattice(unittest.TestCase):

    def setUp(self):
        self.addTypeEqualityFunc(
            LatticeNode, partial(compare_lattice_nodes, testcase=self))

    def test_get_node_on_a_xy_plane_hexagonal_lattice(self):
        # given
        lattice = make_hexagonal_lattice('test', 0.1, 0.2, (5, 4, 6))
        self.add_velocity(lattice)
        vtk_lattice = VTKLattice.from_lattice(lattice)

        # when
        node = vtk_lattice.get_node((1, 1, 0))

        # then
        self.assertEqual(
            node, LatticeNode(
                (1, 1, 0),
                data=DataContainer(VELOCITY=(1, 1, 0))))

    def test_iter_nodes_on_a_xy_plane_hexagonal_lattice(self):
        # given
        lattice = make_hexagonal_lattice('test', 0.1, 0.2, (5, 4, 6))
        self.add_velocity(lattice)
        vtk_lattice = VTKLattice.from_lattice(lattice)

        # when/then
        for node in vtk_lattice.iter_nodes():
            self.assertEqual(
                node, LatticeNode(
                    node.index,
                    data=DataContainer(VELOCITY=node.index)))
        self.assertEqual(sum(1 for _ in vtk_lattice.iter_nodes()), 120)

    def test_update_nodes_on_a_xy_plane_hexagonal_lattice(self):
        # given
        lattice = make_hexagonal_lattice('test', 0.1, 0.2, (5, 4, 6))
        self.add_velocity(lattice)
        vtk_lattice = VTKLattice.from_lattice(lattice)
        node = vtk_lattice.get_node((1, 1, 0))

        # when
        node.data = DataContainer(VELOCITY=(1, 54, 0.3))
        vtk_lattice.update_nodes((node,))

        # then
        new_node = vtk_lattice.get_node((1, 1, 0))
        self.assertEqual(
            new_node, LatticeNode(
                (1, 1, 0),
                data=DataContainer(VELOCITY=(1, 54, 0.3))))

    def test_get_coordinate_on_a_xy_plane_hexagonal_lattice(self):
        # given
        lattice = make_hexagonal_lattice('test', 0.1, 0.2, (5, 4, 6))
        self.add_velocity(lattice)
        vtk_lattice = VTKLattice.from_lattice(lattice)

        # when/then
        for node in lattice.iter_nodes():
            assert_array_equal(
                vtk_lattice.get_coordinate(node.index),
                lattice.get_coordinate(node.index))

    def test_initialization_with_unknown_type(self):
        #
        lattice = make_hexagonal_lattice('test', 0.1, 0.2, (5, 4, 6))
        self.add_velocity(lattice)
        data = VTKLattice.from_lattice(lattice)
        primitive_cell = PrimitiveCell(lattice.primitive_cell.p1,
                                       lattice.primitive_cell.p2,
                                       lattice.primitive_cell.p3,
                                       "Cubic")
        # when/then
        with self.assertRaises(ValueError):
            VTKLattice(
                name=lattice.name, primitive_cell=primitive_cell,
                data_set=data.data_set)

    def test_initialization_with_unfamiliar_dataset(self):
        # given
        data_set = tvtk.UnstructuredGrid(points=[(0, 0, 0,), (1, 1, 1)])
        primitive_cell = PrimitiveCell.for_cubic_lattice(1.)

        # when/then
        with self.assertRaises(TypeError):
            VTKLattice(
                name='test', primitive_cell=primitive_cell,
                data_set=data_set)

    def test_create_empty_with_unknown_type(self):
        primitive_cell = PrimitiveCell((1., 0., 0.), (0., 1., 0.),
                                       (0., 0., 1.), "Cubic")
        # when/then
        with self.assertRaises(ValueError):
            VTKLattice.empty(
                name='test', primitive_cell=primitive_cell, size=(3, 4, 5),
                origin=(0.0, 0.0, 0.0))

    def test_create_from_unfamiliar_dataset(self):
        # given
        data_set = tvtk.UnstructuredGrid(points=[(0, 0, 0,), (1, 1, 1)])

        # when/then
        with self.assertRaises(TypeError):
            VTKLattice.from_dataset(name='test', data_set=data_set)

    @given(lattice_types)
    def test_initialization_with_dataset(self, lattice):
        # given
        expected = VTKLattice.from_lattice(lattice)

        # when
        vtk_lattice = VTKLattice.from_dataset('test', expected.data_set)

        # then
        self.assertEqual(vtk_lattice.primitive_cell.bravais_lattice,
                         lattice.primitive_cell.bravais_lattice)

    @given(lattice_types)
    def test_creating_a_vtk_lattice_from_cuds_lattice(self, lattice):
        # when
        vtk_lattice = VTKLattice.from_lattice(lattice)

        # then
        self.assertEqual(vtk_lattice.primitive_cell.bravais_lattice,
                         lattice.primitive_cell.bravais_lattice)
        self.assertEqual(vtk_lattice.data, lattice.data)
        self.assertEqual(vtk_lattice.size, lattice.size)
        assert_array_equal(vtk_lattice.origin, lattice.origin)
        assert_array_equal(vtk_lattice.primitive_cell.p1,
                           lattice.primitive_cell.p1)
        assert_array_equal(vtk_lattice.primitive_cell.p2,
                           lattice.primitive_cell.p2)
        assert_array_equal(vtk_lattice.primitive_cell.p3,
                           lattice.primitive_cell.p3)

    def test_data_setter(self):
        # when
        primitive_cell = PrimitiveCell.for_cubic_lattice(1.)
        vtk_lattice = VTKLattice.empty('test', primitive_cell, (2, 3, 4),
                                       (0, 0, 0))
        vtk_lattice.data = {CUBA.TEMPERATURE: 40.}

        # then
        self.assertIsInstance(vtk_lattice.data, DataContainer)

    def test_exception_create_dataset_with_inconsistent_lattice_type(self):
        bad_lattice_types = (BravaisLattice.CUBIC,
                             BravaisLattice.TETRAGONAL,
                             BravaisLattice.ORTHORHOMBIC)
        for lattice_type in bad_lattice_types:
            # when
            primitive_cell = PrimitiveCell((1., 0., 0.),  # require PolyData
                                           (0.5, 0.5, 0.),
                                           (0., 0., 1.),
                                           lattice_type)
            lattice = Lattice('test', primitive_cell, (2, 3, 4),
                              (0., 0., 0.))

            # then
            with self.assertRaises(ValueError):
                vtk_lattice = VTKLattice.from_lattice(lattice)

    def add_velocity(self, lattice):
        new_nodes = []
        for node in lattice.iter_nodes():
            node.data[CUBA.VELOCITY] = node.index
            new_nodes.append(node)
        lattice.update_nodes(new_nodes)


if __name__ == '__main__':
    unittest.main()
