import itertools
import unittest
import tempfile
import shutil
import os

import numpy
from numpy.testing import assert_array_equal
from mayavi.core.api import NullEngine
from mayavi import __version__ as MAYAVI_VERSION
from mayavi import mlab

from simphony.cuds.mesh import Mesh, Point, Cell, Edge, Face
from simphony.cuds.particles import Particle, Particles, Bond
from simphony.cuds.primitive_cell import PrimitiveCell
from simphony.cuds.lattice import (
    Lattice, make_hexagonal_lattice, make_cubic_lattice,
    make_orthorhombic_lattice)
from simphony.core.data_container import DataContainer
from simphony.core.cuba import CUBA

from simphony_mayavi.cuds.api import VTKMesh, VTKLattice, VTKParticles
from simphony_mayavi.core.api import (
    cell_array_slicer,
    CELL2VTKCELL, FACE2VTKCELL, EDGE2VTKCELL)
from simphony_mayavi.sources.slim_cuds_source import SlimCUDSSource, \
    _available_keys
from simphony_mayavi.sources.tests.test_cuds_source import TestParticlesSource, \
    TestLatticeSource, TestMeshSource


class TestMeshSlimSource(TestMeshSource):
    tested_class = SlimCUDSSource

    def test_points(self):
        # given
        container = self.container

        # when
        source = self.tested_class(cuds=container)

        # then
        number_of_points = len(self.points)
        vtk_cuds = source._vtk_cuds
        vtk_dataset = source.data
        points = source.data.points.to_array()
        self.assertEqual(len(points), number_of_points)
        self.assertEqual(len(vtk_cuds.point2index), number_of_points)
        self.assertEqual(vtk_dataset.point_data.number_of_arrays, 0)

        source.point_scalars_name = 'TEMPERATURE'
        vtk_dataset = source.data
        self.assertEqual(vtk_dataset.point_data.number_of_arrays, 1)

        temperature = vtk_dataset.point_data.get_array('TEMPERATURE')
        for key, index in vtk_cuds.point2index.iteritems():
            point = container.get_point(key)
            assert_array_equal(points[index], point.coordinates)
            self.assertEqual(temperature[index], point.data[CUBA.TEMPERATURE])

    def test_cells(self):
        # given
        container = self.container
        cell_iter = (Cell(points=[self.point_uids[index] for index in cell],
                          data=DataContainer(TEMPERATURE=i))
                     for i, cell in enumerate(self.cells))
        container.add_cells(cell_iter)

        # when
        source = self.tested_class(cuds=container)
        vtk_dataset = source.data
        vtk_cuds = source._vtk_cuds
        number_of_cells = len(self.cells)
        cells = [
            cell
            for cell in cell_array_slicer(vtk_dataset.get_cells().to_array())]
        self.assertEqual(len(cells), number_of_cells)
        self.assertEqual(len(vtk_cuds.element2index), number_of_cells)
        self.assertEqual(source.data.cell_data.number_of_arrays, 0)

        source.cell_scalars_name = 'TEMPERATURE'
        vtk_dataset = source.data
        self.assertEqual(vtk_dataset.cell_data.number_of_arrays, 1)

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
        edge_iter = (Edge(points=[self.point_uids[index] for index in edge],
                          data=DataContainer(TEMPERATURE=i))
                     for i, edge in enumerate(self.edges))
        container.add_edges(edge_iter)

        # when
        source = self.tested_class(cuds=container)

        # then
        vtk_dataset = source.data
        vtk_cuds = source._vtk_cuds
        edges = [
            edge
            for edge in cell_array_slicer(vtk_dataset.get_cells().to_array())]
        number_of_edges = len(self.edges)
        self.assertEqual(len(edges), number_of_edges)
        self.assertEqual(len(vtk_cuds.element2index), number_of_edges)
        self.assertEqual(source.data.cell_data.number_of_arrays, 0)

        source.cell_scalars_name = 'TEMPERATURE'
        vtk_dataset = source.data

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
        face_iter = (Face(points=[self.point_uids[index] for index in face],
                          data=DataContainer(TEMPERATURE=i))
                     for i, face in enumerate(self.faces))
        container.add_faces(face_iter)

        # when
        source = self.tested_class(cuds=container)

        # then
        vtk_cuds = source._vtk_cuds
        vtk_dataset = source.data
        faces = [
            face
            for face in cell_array_slicer(vtk_dataset.get_cells().to_array())]
        number_of_faces = len(self.faces)
        self.assertEqual(len(faces), number_of_faces)
        self.assertEqual(len(vtk_cuds.element2index), number_of_faces)
        self.assertEqual(source.data.cell_data.number_of_arrays, 0)
        source.cell_scalars_name = 'TEMPERATURE'
        vtk_dataset = source.data
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
        face_iter = (Face(points=[self.point_uids[index] for index in face],
                          data=DataContainer(TEMPERATURE=next(count)))
                     for face in self.faces)
        container.add_faces(face_iter)

        edge_iter = (Edge(points=[self.point_uids[index] for index in edge],
                          data=DataContainer(TEMPERATURE=next(count)))
                     for edge in self.edges)
        container.add_edges(edge_iter)

        cell_iter = (Cell(points=[self.point_uids[index] for index in cell],
                          data=DataContainer(TEMPERATURE=next(count)))
                     for cell in self.cells)
        container.add_cells(cell_iter)

        # when
        source = self.tested_class(cuds=container)
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

        source.point_scalars_name = 'TEMPERATURE'
        source.cell_scalars_name = 'TEMPERATURE'
        vtk_dataset = source.data

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


class TestParticlesSlimSource(TestParticlesSource):
    tested_class = SlimCUDSSource

    def setUp(self):
        self.points = [
            [0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
        self.bonds = [[0, 1], [0, 3], [1, 3, 2]]
        self.point_temperature = [10., 20., 30., 40.]
        self.point_radius = [1., 2., 3., 4.]
        self.point_mass = [4., 8., 16., 32.]
        self.bond_temperature = [60., 80., 190., 5.]

        self.container = Particles('test')

        # add particles
        def particle_iter():
            for temp, radius, mass, point in zip(
                    self.point_temperature,
                    self.point_radius,
                    self.point_mass,
                    self.points):
                yield Particle(coordinates=point,
                               data=DataContainer(
                                   TEMPERATURE=temp,
                                   RADIUS=radius,
                                   MASS=mass))

        self.point_uids = self.container.add_particles(particle_iter())

        # add bonds
        def bond_iter():
            for temp, indices in zip(self.bond_temperature, self.bonds):
                yield Bond(particles=[self.point_uids[index]
                                      for index in indices],
                           data=DataContainer(
                               TEMPERATURE=temp,
                               ))

        self.bond_uids = self.container.add_bonds(bond_iter())

        # for testing save/load visualization
        self.temp_dir = tempfile.mkdtemp()

    def test_particles(self):
        cuds = self.container

        source = SlimCUDSSource(cuds=cuds)

        self.assertEqual(len(source._point_scalars_list), 4)
        for entry in ['', 'MASS', 'RADIUS', 'TEMPERATURE']:
            self.assertIn(entry, source._point_scalars_list)

        dataset = source.data
        self.assertEqual(dataset.point_data.number_of_arrays, 0)
        self.assertEqual(source.point_scalars_name, '')

        source.point_scalars_name = "TEMPERATURE"
        dataset = source.data
        points = dataset.points.to_array()
        vtk_cuds = source._vtk_cuds

        self.assertEqual(dataset.point_data.number_of_arrays, 1)
        temperature = dataset.point_data.get_array('TEMPERATURE')
        for key, index in vtk_cuds.particle2index.iteritems():
            point = self.container.get_particle(key)
            assert_array_equal(points[index], point.coordinates)
            self.assertEqual(temperature[index], point.data[CUBA.TEMPERATURE])

        source.point_scalars_name = "MASS"
        self.assertEqual(dataset.point_data.number_of_arrays, 1)
        dataset = source.data
        mass = dataset.point_data.get_array('MASS')
        for key, index in vtk_cuds.particle2index.iteritems():
            point = self.container.get_particle(key)
            assert_array_equal(points[index], point.coordinates)
            self.assertEqual(mass[index], point.data[CUBA.MASS])

        source.point_scalars_name = ""
        dataset = source.data
        self.assertEqual(dataset.point_data.number_of_arrays, 0)

    def test_available_keys(self):
        (point_scalars,
         point_vectors,
         cell_scalars,
         cell_vectors) = _available_keys(self.container)

        self.assertEqual(point_scalars, {CUBA.TEMPERATURE,
                                         CUBA.RADIUS,
                                         CUBA.MASS})

        self.assertEqual(point_vectors, set())
        self.assertEqual(cell_scalars, {CUBA.TEMPERATURE})
        self.assertEqual(cell_vectors, set())

    def test_bonds(self):
        source = SlimCUDSSource(cuds=self.container)

        # We should have two entries in the available cuba data, one for
        # temperature and one for blank
        self.assertEqual(len(source._cell_scalars_list), 2)
        for entry in ['', 'TEMPERATURE']:
            self.assertIn(entry, source._cell_scalars_list)

        dataset = source.data
        # The actual array set in the cell data should be empty if selection
        # is blank
        self.assertEqual(dataset.cell_data.number_of_arrays, 0)
        self.assertEqual(source.cell_scalars_name, '')

        # Selecting temperature triggers the transfer from cuds to vtk cuds
        # of only the selected array
        source.cell_scalars_name = "TEMPERATURE"
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
            bond = self.container.get_bond(key)
            particles = [
                vtk_cuds.particle2index[uid] for uid in bond.particles]
            self.assertEqual(bonds[index], particles)
            self.assertEqual(temperature[index], bond.data[CUBA.TEMPERATURE])

        # Clearing should empty the data again
        source.cell_scalars_name = ""
        dataset = source.data
        self.assertEqual(dataset.cell_data.number_of_arrays, 0)

    @unittest.skip("Cannot perform save/load with SlimCUDSSource")
    def test_save_load_visualization_with_mlab(self):
        pass

    @unittest.skip("Cannot perform save/load with SlimCUDSSource")
    def test_save_load_visualization_with_null_engine(self):
        pass

class TestLatticeSlimSource(TestLatticeSource):
    tested_class = SlimCUDSSource

    def test_source_from_a_cubic_lattice(self):
        cuds = make_cubic_lattice('test', 0.4, (14, 24, 34), (4, 5, 6))
        self._add_velocity(cuds)
        source = SlimCUDSSource(cuds=cuds)
        data = source.data
        self.assertEqual(data.number_of_points, 14 * 24 * 34)
        assert_array_equal(data.origin, (4.0, 5.0, 6.0))

        self.assertEqual(data.point_data.number_of_arrays, 0)
        self.assertEqual(len(source._point_vectors_list), 2)
        self.assertEqual(source._point_vectors_list, ['', 'VELOCITY'])
        self.assertEqual(source.point_vectors_name, '')

        source.point_vectors_name = 'VELOCITY'
        data = source.data
        self.assertEqual(data.point_data.number_of_arrays, 1)
        vectors = data.point_data.vectors.to_array()

        for node in cuds.iter_nodes():
            point_id = data.compute_point_id(node.index)
            assert_array_equal(
                cuds.get_coordinate(node.index),
                data.get_point(point_id))
            assert_array_equal(vectors[point_id], node.index)

        source.point_vectors_name = ''
        data = source.data
        self.assertEqual(data.point_data.number_of_arrays, 0)

    def test_source_from_an_orthorombic_p_lattice(self):
        cuds = make_orthorhombic_lattice(
            'test',  (0.5, 0.54, 0.58), (15, 25, 35), (7, 9, 8))
        self._add_velocity(cuds)
        source = SlimCUDSSource(cuds=cuds)
        data = source.data
        self.assertEqual(data.number_of_points, 15 * 25 * 35)
        assert_array_equal(data.origin, (7.0, 9.0, 8.0))

        self.assertEqual(data.point_data.number_of_arrays, 0)
        self.assertEqual(len(source._point_vectors_list), 2)
        self.assertEqual(source._point_vectors_list, ['', 'VELOCITY'])
        self.assertEqual(source.point_vectors_name, '')

        source.point_vectors_name = 'VELOCITY'
        data = source.data
        self.assertEqual(data.point_data.number_of_arrays, 1)

        vectors = data.point_data.vectors.to_array()
        for node in cuds.iter_nodes():
            point_id = data.compute_point_id(node.index)
            assert_array_equal(
                cuds.get_coordinate(node.index),
                data.get_point(point_id))
            assert_array_equal(vectors[point_id], node.index)

        source.point_vectors_name = ''
        data = source.data
        self.assertEqual(data.point_data.number_of_arrays, 0)

    def test_source_from_a_xy_plane_hexagonal_lattice(self):
        xspace = 0.1
        yspace = 0.1*numpy.sqrt(3.)/2.
        cuds = make_hexagonal_lattice('test', xspace, 0.2, (5, 4, 1))
        self._add_velocity(cuds)
        source = SlimCUDSSource(cuds=cuds)
        data = source.data
        self.assertEqual(data.number_of_points, 5 * 4 * 1)

        self.assertEqual(data.point_data.number_of_arrays, 0)
        self.assertEqual(len(source._point_vectors_list), 2)
        self.assertEqual(source._point_vectors_list, ['', 'VELOCITY'])
        self.assertEqual(source.point_vectors_name, '')

        source.point_vectors_name = 'VELOCITY'
        data = source.data
        self.assertEqual(data.point_data.number_of_arrays, 1)

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
        for node in cuds.iter_nodes():
            position = (
                node.index[0] * xspace + 0.5 * xspace * node.index[1],
                node.index[1] * yspace,
                0.0)
            point_id = data.find_point(position)
            assert_array_equal(vectors[point_id], node.index)

    def _add_velocity(self, lattice):
        new_nodes = []
        for node in lattice.iter_nodes():
            node.data[CUBA.VELOCITY] = node.index
            new_nodes.append(node)
        lattice.update_nodes(new_nodes)

