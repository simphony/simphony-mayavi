import unittest

import numpy
from numpy.testing import assert_array_equal

from simphony.cuds.mesh import Mesh, Point, Cell, Edge, Face
from simphony_mayavi.sources.api import MeshSource, cell_array_slicer
from simphony_mayavi.sources.mesh_source import (
    CELL2VTKCELL, FACE2VTKCELL, EDGE2VTKCELL)


class TestParticlesSource(unittest.TestCase):

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
            container.add_point(Point(coordinates=point)) for point in points]

    def test_points(self):
        container = self.container
        source = MeshSource.from_mesh(container)
        points = source.data.points.to_array()

        number_of_points = len(self.points)
        self.assertEqual(len(points), number_of_points)
        self.assertEqual(len(source.point2index), number_of_points)

        for key, index in source.point2index.iteritems():
            point = container.get_point(key)
            assert_array_equal(points[index], point.coordinates)

    def test_cells(self):
        container = self.container
        for cell in self.cells:
            container.add_cell(
                Cell(points=[self.point_uids[index] for index in cell]))

        source = MeshSource.from_mesh(container)
        vtk_source = source.data
        cells = [
            cell
            for cell in cell_array_slicer(vtk_source.get_cells().to_array())]

        number_of_cells = len(self.cells)
        self.assertEqual(len(cells), number_of_cells)
        self.assertEqual(len(source.element2index), number_of_cells)

        for key, index in source.element2index.iteritems():
            cell = container.get_cell(key)
            self.assertEqual(
                vtk_source.get_cell_type(index),
                CELL2VTKCELL[len(cell.points)])
            points = [source.point2index[uid] for uid in cell.points]
            self.assertEqual(cells[index], points)

    def test_edges(self):
        container = self.container
        for edge in self.edges:
            container.add_edge(
                Edge(points=[self.point_uids[index] for index in edge]))

        source = MeshSource.from_mesh(container)
        vtk_source = source.data
        edges = [
            edge
            for edge in cell_array_slicer(vtk_source.get_cells().to_array())]

        number_of_edges = len(self.edges)
        self.assertEqual(len(edges), number_of_edges)
        self.assertEqual(len(source.element2index), number_of_edges)

        for key, index in source.element2index.iteritems():
            edge = container.get_edge(key)
            self.assertEqual(
                vtk_source.get_cell_type(index),
                EDGE2VTKCELL[len(edge.points)])
            points = [source.point2index[uid] for uid in edge.points]
            self.assertEqual(edges[index], points)

    def test_face(self):
        container = self.container
        for face in self.faces:
            container.add_face(
                Face(points=[self.point_uids[index] for index in face]))

        source = MeshSource.from_mesh(container)
        vtk_source = source.data
        faces = [
            face
            for face in cell_array_slicer(vtk_source.get_cells().to_array())]

        number_of_faces = len(self.faces)
        self.assertEqual(len(faces), number_of_faces)
        self.assertEqual(len(source.element2index), number_of_faces)

        for key, index in source.element2index.iteritems():
            face = container.get_face(key)
            self.assertEqual(
                vtk_source.get_cell_type(index),
                FACE2VTKCELL[len(face.points)])
            points = [source.point2index[uid] for uid in face.points]
            self.assertEqual(faces[index], points)

    def test_all_element_types(self):
        container = self.container
        for face in self.faces:
            container.add_face(
                Face(points=[self.point_uids[index] for index in face]))
        for edge in self.edges:
            container.add_edge(
                Edge(points=[self.point_uids[index] for index in edge]))
        for cell in self.cells:
            container.add_cell(
                Cell(points=[self.point_uids[index] for index in cell]))

        source = MeshSource.from_mesh(container)
        vtk_source = source.data
        elements = [
            element
            for element in cell_array_slicer(
                vtk_source.get_cells().to_array())]

        number_of_elements = \
            len(self.faces) + len(self.edges) + len(self.cells)
        self.assertEqual(len(elements), number_of_elements)
        self.assertEqual(len(source.element2index), number_of_elements)
        for key, index in source.element2index.iteritems():
            cell_type = vtk_source.get_cell_type(index)
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
            points = [source.point2index[uid] for uid in element.points]
            self.assertEqual(elements[index], points)
