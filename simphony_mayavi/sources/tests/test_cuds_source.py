import itertools
import unittest

import numpy
from numpy.testing import assert_array_equal
from simphony.cuds.mesh import Mesh, Point, Cell, Edge, Face
from simphony.cuds.particles import Particle, Particles, Bond
from simphony.cuds.lattice import (
    Lattice, make_hexagonal_lattice, make_square_lattice,
    make_cubic_lattice, make_rectangular_lattice, make_orthorombicp_lattice)
from simphony.core.data_container import DataContainer
from simphony.core.cuba import CUBA

from simphony_mayavi.cuds.api import VTKMesh, VTKLattice, VTKParticles
from simphony_mayavi.core.api import (
    cell_array_slicer,
    CELL2VTKCELL, FACE2VTKCELL, EDGE2VTKCELL)
from simphony_mayavi.sources.api import CUDSSource


class TestMeshSource(unittest.TestCase):

    def setUp(self):
        self.points = points = numpy.array([
            [0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1],
            [2, 0, 0], [3, 0, 0], [3, 1, 0], [2, 1, 0],
            [2, 0, 1], [3, 0, 1], [3, 1, 1], [2, 1, 1]],
            'f')

        self.cells = [
            [0, 1, 2, 3],  # tetra
            [4, 5, 6, 7, 8, 9, 10, 11]]  # hex
        self.faces = [[2, 7, 11]]
        self.edges = [[1, 4], [3, 8]]
        self.container = container = Mesh('test')
        self.point_uids = [
            container.add_point(
                Point(coordinates=point,
                      data=DataContainer(TEMPERATURE=index)))
            for index, point in enumerate(points)]

    def test_points(self):
        # given
        container = self.container

        # when
        source = CUDSSource(cuds=container)

        # then
        number_of_points = len(self.points)
        vtk_cuds = source._vtk_cuds
        vtk_dataset = source.data
        points = source.data.points.to_array()
        self.assertEqual(len(points), number_of_points)
        self.assertEqual(len(vtk_cuds.point2index), number_of_points)
        self.assertEqual(vtk_dataset.point_data.number_of_arrays, 1)
        temperature = vtk_dataset.point_data.get_array('TEMPERATURE')
        for key, index in vtk_cuds.point2index.iteritems():
            point = container.get_point(key)
            assert_array_equal(points[index], point.coordinates)
            self.assertEqual(temperature[index], point.data[CUBA.TEMPERATURE])

    def test_cells(self):
        # given
        container = self.container
        for i, cell in enumerate(self.cells):
            container.add_cell(
                Cell(
                    points=[self.point_uids[index] for index in cell],
                    data=DataContainer(TEMPERATURE=i)))

        # when
        source = CUDSSource(cuds=container)
        vtk_dataset = source.data
        vtk_cuds = source._vtk_cuds
        number_of_cells = len(self.cells)
        cells = [
            cell
            for cell in cell_array_slicer(vtk_dataset.get_cells().to_array())]
        self.assertEqual(len(cells), number_of_cells)
        self.assertEqual(len(vtk_cuds.element2index), number_of_cells)
        self.assertEqual(source.data.cell_data.number_of_arrays, 1)
        temperature = source.data.cell_data.get_array('TEMPERATURE')
        for key, index in vtk_cuds.element2index.iteritems():
            cell = container.get_cell(key)
            self.assertEqual(
                vtk_dataset.get_cell_type(index),
                CELL2VTKCELL[len(cell.points)])
            points = [vtk_cuds.point2index[uid] for uid in cell.points]
            self.assertEqual(cells[index], points)
            self.assertEqual(temperature[index], cell.data[CUBA.TEMPERATURE])

    def test_edges(self):
        # given
        container = self.container
        for i, edge in enumerate(self.edges):
            container.add_edge(
                Edge(
                    points=[self.point_uids[index] for index in edge],
                    data=DataContainer(TEMPERATURE=i)))

        # when
        source = CUDSSource(cuds=container)

        # then
        vtk_dataset = source.data
        vtk_cuds = source._vtk_cuds
        edges = [
            edge
            for edge in cell_array_slicer(vtk_dataset.get_cells().to_array())]
        number_of_edges = len(self.edges)
        self.assertEqual(len(edges), number_of_edges)
        self.assertEqual(len(vtk_cuds.element2index), number_of_edges)
        self.assertEqual(vtk_dataset.cell_data.number_of_arrays, 1)
        temperature = vtk_dataset.cell_data.get_array('TEMPERATURE')
        for key, index in vtk_cuds.element2index.iteritems():
            edge = container.get_edge(key)
            self.assertEqual(
                vtk_dataset.get_cell_type(index),
                EDGE2VTKCELL[len(edge.points)])
            points = [vtk_cuds.point2index[uid] for uid in edge.points]
            self.assertEqual(edges[index], points)
            self.assertEqual(temperature[index], edge.data[CUBA.TEMPERATURE])

    def test_face(self):
        # given
        container = self.container
        for i, face in enumerate(self.faces):
            container.add_face(
                Face(
                    points=[self.point_uids[index] for index in face],
                    data=DataContainer(TEMPERATURE=i)))

        # when
        source = CUDSSource(cuds=container)

        # then
        vtk_cuds = source._vtk_cuds
        vtk_dataset = source.data
        faces = [
            face
            for face in cell_array_slicer(vtk_dataset.get_cells().to_array())]
        number_of_faces = len(self.faces)
        self.assertEqual(len(faces), number_of_faces)
        self.assertEqual(len(vtk_cuds.element2index), number_of_faces)

        self.assertEqual(vtk_dataset.cell_data.number_of_arrays, 1)
        temperature = vtk_dataset.cell_data.get_array('TEMPERATURE')
        for key, index in vtk_cuds.element2index.iteritems():
            face = container.get_face(key)
            self.assertEqual(
                vtk_dataset.get_cell_type(index),
                FACE2VTKCELL[len(face.points)])
            points = [vtk_cuds.point2index[uid] for uid in face.points]
            self.assertEqual(faces[index], points)
            self.assertEqual(temperature[index], face.data[CUBA.TEMPERATURE])

    def test_all_element_types(self):
        # given
        container = self.container
        count = itertools.count()
        for face in self.faces:
            container.add_face(
                Face(
                    points=[self.point_uids[index] for index in face],
                    data=DataContainer(TEMPERATURE=next(count))))
        for edge in self.edges:
            container.add_edge(
                Edge(
                    points=[self.point_uids[index] for index in edge],
                    data=DataContainer(TEMPERATURE=next(count))))
        for cell in self.cells:
            container.add_cell(
                Cell(
                    points=[self.point_uids[index] for index in cell],
                    data=DataContainer(TEMPERATURE=next(count))))

        # when
        source = CUDSSource(cuds=container)
        vtk_dataset = source.data
        vtk_cuds = source._vtk_cuds
        elements = [
            element
            for element in cell_array_slicer(
                vtk_dataset.get_cells().to_array())]
        number_of_elements = \
            len(self.faces) + len(self.edges) + len(self.cells)
        self.assertEqual(len(elements), number_of_elements)
        self.assertEqual(len(vtk_cuds.element2index), number_of_elements)
        self.assertEqual(source.data.point_data.number_of_arrays, 1)
        self.assertEqual(source.data.cell_data.number_of_arrays, 1)
        temperature = source.data.cell_data.get_array('TEMPERATURE')
        for key, index in vtk_cuds.element2index.iteritems():
            cell_type = vtk_dataset.get_cell_type(index)
            if cell_type in EDGE2VTKCELL.values():
                element = container.get_edge(key)
                self.assertEqual(
                    cell_type, EDGE2VTKCELL[len(element.points)])
            elif cell_type in FACE2VTKCELL.values():
                element = container.get_face(key)
                self.assertEqual(
                    cell_type, FACE2VTKCELL[len(element.points)])
            elif cell_type in CELL2VTKCELL.values():
                element = container.get_cell(key)
                self.assertEqual(
                    cell_type, CELL2VTKCELL[len(element.points)])
            else:
                self.fail('vtk source has an unknown cell type')
            points = [vtk_cuds.point2index[uid] for uid in element.points]
            self.assertEqual(elements[index], points)
            self.assertEqual(
                temperature[index], element.data[CUBA.TEMPERATURE])

    def test_mesh_source_from_vtk_mesh(self):
        # given
        container = self.container
        vtk_container = VTKMesh.from_mesh(container)

        # when
        source = CUDSSource(cuds=vtk_container)

        # then
        vtk_cuds = source._vtk_cuds
        self.assertIs(source.data, vtk_container.data_set)
        self.assertIs(vtk_cuds, vtk_container)


class TestLatticeSource(unittest.TestCase):

    def test_source_from_a_xy_plane_square_lattice(self):
        shape = 2, 4
        lattice = make_square_lattice(
            'test', 0.2, (2, 4), origin=(0.2, -2.4, 0.0))
        self.add_velocity(lattice)
        source = CUDSSource(cuds=lattice)
        data = source.data
        self.assertEqual(data.number_of_points, numpy.prod(shape))
        assert_array_equal(data.origin, (0.2, -2.4, 0.0))

        vectors = data.point_data.vectors.to_array()
        for node in lattice.iter_nodes():
            index = numpy.array(node.index)
            point_id = data.compute_point_id(index)
            assert_array_equal(
                lattice.get_coordinate(node.index),
                data.get_point(point_id))
            assert_array_equal(vectors[point_id], index)

    def test_source_from_a_xy_plane_rectangular_lattice(self):
        lattice = make_rectangular_lattice(
            'test', (0.3, 0.35), (13, 23), origin=(0.2, -2.7, 0.0))
        self.add_velocity(lattice)
        source = CUDSSource(cuds=lattice)
        data = source.data
        self.assertEqual(data.number_of_points, 13 * 23)
        assert_array_equal(data.origin, (0.2, -2.7, 0.0))

        vectors = data.point_data.vectors.to_array()
        for node in lattice.iter_nodes():
            index = numpy.array(node.index)
            point_id = data.compute_point_id(index)
            assert_array_equal(
                lattice.get_coordinate(node.index),
                data.get_point(point_id))
            assert_array_equal(vectors[point_id], index)

    def test_source_from_a_cubic_lattice(self):
        lattice = make_cubic_lattice('test', 0.4, (14, 24, 34), (4, 5, 6))
        self.add_velocity(lattice)
        source = CUDSSource(cuds=lattice)
        data = source.data
        self.assertEqual(data.number_of_points, 14 * 24 * 34)
        assert_array_equal(data.origin, (4.0, 5.0, 6.0))

        vectors = data.point_data.vectors.to_array()
        for node in lattice.iter_nodes():
            point_id = data.compute_point_id(node.index)
            assert_array_equal(
                lattice.get_coordinate(node.index),
                data.get_point(point_id))
            assert_array_equal(vectors[point_id], node.index)

    def test_source_from_an_orthorombic_p_lattice(self):
        lattice = make_orthorombicp_lattice(
            'test',  (0.5, 0.54, 0.58), (15, 25, 35), (7, 9, 8))
        self.add_velocity(lattice)
        source = CUDSSource(cuds=lattice)
        data = source.data
        self.assertEqual(data.number_of_points, 15 * 25 * 35)
        assert_array_equal(data.origin, (7.0, 9.0, 8.0))

        vectors = data.point_data.vectors.to_array()
        for node in lattice.iter_nodes():
            point_id = data.compute_point_id(node.index)
            assert_array_equal(
                lattice.get_coordinate(node.index),
                data.get_point(point_id))
            assert_array_equal(vectors[point_id], node.index)

    def test_source_from_a_xy_plane_hexagonal_lattice(self):
        lattice = make_hexagonal_lattice('test', 0.1, (5, 4))
        self.add_velocity(lattice)
        source = CUDSSource(cuds=lattice)
        data = source.data
        self.assertEqual(data.number_of_points, 5 * 4)
        xspace, yspace, _ = lattice.base_vect

        for index, point in enumerate(data.points):
            # The lattice has 4 rows (y axis) and 5 columns (x axis).
            # Thus the correct size to unravel is (4, 5) instead of
            # (5, 4).
            row, column = numpy.unravel_index(index,  (4, 5))
            assert_array_equal(
                point, (
                    xspace * column + 0.5 * xspace * row,
                    yspace * row,
                    0.0))

        vectors = data.point_data.vectors.to_array()
        for node in lattice.iter_nodes():
            position = (
                node.index[0] * xspace + 0.5 * xspace * node.index[1],
                node.index[1] * yspace,
                0.0)
            point_id = data.find_point(position)
            assert_array_equal(vectors[point_id], node.index)

    def test_source_from_unknown(self):
        lattice = Lattice('test', '', (1, 1, 1), (1, 1, 1), (0, 0, 0))
        with self.assertRaises(ValueError):
            CUDSSource(cuds=lattice)

    def test_source_from_a_vtk_lattice(self):
        # given
        lattice = VTKLattice.empty(
            'test', 'Cubic', (0.1, 0.1, 0.1), (5, 10, 12), (0, 0, 0))

        # when
        source = CUDSSource(cuds=lattice)

        # then
        self.assertIs(source._vtk_cuds, lattice)
        self.assertIs(source.data, lattice.data_set)

    def add_velocity(self, lattice):
        for node in lattice.iter_nodes():
            node.data[CUBA.VELOCITY] = node.index
            lattice.update_node(node)


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

    def test_source_from_vtk_particles(self):
        # given
        container = VTKParticles('test')
        for particle in self.container.iter_particles():
            container.add_particle(particle)
        for bond in self.container.iter_bonds():
            container.add_bond(bond)

        # when
        source = CUDSSource(cuds=container)

        # then
        self.assertIs(source.data, container.data_set)
        self.assertIs(source.cuds, container)

    def test_particles(self):
        # given
        container = self.container

        # when
        source = CUDSSource(cuds=container)

        # then
        points = source.data.points.to_array()
        dataset = source.data
        vtk_cuds = source._vtk_cuds

        number_of_particles = len(self.points)
        self.assertEqual(len(points), number_of_particles)
        self.assertEqual(len(vtk_cuds.particle2index), number_of_particles)
        self.assertEqual(dataset.point_data.number_of_arrays, 1)
        temperature = dataset.point_data.get_array('TEMPERATURE')
        for key, index in vtk_cuds.particle2index.iteritems():
            point = container.get_particle(key)
            assert_array_equal(points[index], point.coordinates)
            self.assertEqual(temperature[index], point.data[CUBA.TEMPERATURE])

    def test_bonds(self):
        # given
        container = self.container

        # when
        source = CUDSSource(cuds=container)

        # then
        dataset = source.data
        vtk_cuds = source._vtk_cuds
        bonds = [
            bond for bond in cell_array_slicer(dataset.lines.to_array())]
        number_of_bonds = len(self.bonds)
        self.assertEqual(len(bonds), number_of_bonds)
        self.assertEqual(len(vtk_cuds.bond2index), number_of_bonds)
        self.assertEqual(dataset.cell_data.number_of_arrays, 1)
        temperature = dataset.cell_data.get_array('TEMPERATURE')
        for key, index in vtk_cuds.bond2index.iteritems():
            bond = container.get_bond(key)
            particles = [vtk_cuds.particle2index[uid] for uid in bond.particles]
            self.assertEqual(bonds[index], particles)
            self.assertEqual(temperature[index], bond.data[CUBA.TEMPERATURE])
