import unittest
import itertools
from functools import partial

import numpy
from tvtk.api import tvtk

from simphony.cuds.mesh import Mesh, Point, Face, Edge, Cell
from simphony.core.data_container import DataContainer
from simphony.core.cuba import CUBA
from simphony.core.cuds_item import CUDSItem
from simphony.testing.abc_check_mesh import (
    CheckMeshContainer, CheckMeshItemOperations,
    CheckMeshPointOperations, CheckMeshElementOperations,
    CheckMeshEdgeOperations, CheckMeshFaceOperations,
    CheckMeshCellOperations)
from simphony.testing.utils import (compare_data_containers,
                                    compare_points, compare_elements)


from simphony_mayavi.cuds.api import VTKMesh
from simphony_mayavi.core.api import supported_cuba as mayavi_supported_cuba


def vtk_compare_points(point, reference, msg=None, testcase=None):
    ''' use numpy.allclose to compare point coordinates retrieved
    from vtk dataset with the reference as vtk casts coordinates to
    double-precision floats and precision errors may be introduced
    during casting
    '''
    self = testcase
    self.assertEqual(point.uid, reference.uid)
    if not numpy.allclose(point.coordinates, reference.coordinates):
        error_message = "{} != {}"
        self.failureException(error_message.format(point, reference))
    compare_data_containers(point.data, reference.data, testcase=self)


class TestVTKMeshContainer(CheckMeshContainer, unittest.TestCase):

    def supported_cuba(self):
        return set(CUBA)

    def container_factory(self, name):
        return VTKMesh(name=name)


class TestVTKMeshPointOperations(CheckMeshPointOperations, unittest.TestCase):

    def setUp(self):
        CheckMeshItemOperations.setUp(self)
        self.addTypeEqualityFunc(
            Point, partial(vtk_compare_points, testcase=self))

    def create_items(self):
        return create_points(restrict=self.supported_cuba())

    def supported_cuba(self):
        return mayavi_supported_cuba()

    def container_factory(self, name):
        return VTKMesh(name=name)


class TestVTKMeshEdgeOperations(CheckMeshEdgeOperations, unittest.TestCase):

    def supported_cuba(self):
        return mayavi_supported_cuba()

    def container_factory(self, name):
        container = VTKMesh(name=name)
        return container


class TestVTKMeshFaceOperations(CheckMeshFaceOperations, unittest.TestCase):

    def supported_cuba(self):
        return mayavi_supported_cuba()

    def container_factory(self, name):
        container = VTKMesh(name=name)
        return container


class TestVTKMeshCellOperations(CheckMeshCellOperations, unittest.TestCase):

    def supported_cuba(self):
        return mayavi_supported_cuba()

    def container_factory(self, name):
        container = VTKMesh(name=name)
        return container


class TestVTKMesh(unittest.TestCase):

    def setUp(self):
        self.addTypeEqualityFunc(
            Point, partial(compare_points, testcase=self))
        self.addTypeEqualityFunc(
            Edge, partial(compare_elements, testcase=self))
        self.addTypeEqualityFunc(
            Face, partial(compare_elements, testcase=self))
        self.addTypeEqualityFunc(
            Cell, partial(compare_elements, testcase=self))
        self.points = numpy.array([
            [0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1],
            [2, 0, 0], [3, 0, 0], [3, 1, 0], [2, 1, 0],
            [2, 0, 1], [3, 0, 1], [3, 1, 1], [2, 1, 1]],
            'f')
        self.cells = [
            [0, 1, 2, 3],  # tetra
            [4, 5, 6, 7, 8, 9, 10, 11]]  # hex
        self.faces = [[2, 7, 11]]
        self.edges = [[1, 4], [3, 8]]

    def test_initialization_from_cuds(self):
        # given
        count = itertools.count()
        points = [
            Point(coordinates=point, data=DataContainer(TEMPERATURE=index))
            for index, point in enumerate(self.points)]

        container = Mesh('test')
        container.add_points(points)

        faces = [
            Face(
                points=[points[index].uid for index in face],
                data=DataContainer(TEMPERATURE=next(count)))
            for face in self.faces]
        edges = [
            Edge(
                points=[points[index].uid for index in edge],
                data=DataContainer(TEMPERATURE=next(count)))
            for edge in self.edges]
        cells = [
            Cell(
                points=[points[index].uid for index in cell],
                data=DataContainer(TEMPERATURE=next(count)))
            for cell in self.cells]
        container.add_edges(edges)
        container.add_faces(faces)
        container.add_cells(cells)

        # when
        vtk_container = VTKMesh.from_mesh(container)

        # then
        self.assertEqual(vtk_container.name, container.name)
        self.assertEqual(sum(1 for _ in vtk_container.iter_points()), 12)
        self.assertEqual(sum(1 for _ in vtk_container.iter_edges()), 2)
        self.assertEqual(sum(1 for _ in vtk_container.iter_faces()), 1)
        self.assertEqual(sum(1 for _ in vtk_container.iter_cells()), 2)
        for point in points:
            self.assertEqual(vtk_container.get_point(point.uid), point)
        for edge in edges:
            self.assertEqual(vtk_container.get_edge(edge.uid), edge)
        for face in faces:
            self.assertEqual(vtk_container.get_face(face.uid), face)
        for cell in cells:
            self.assertEqual(vtk_container.get_cell(cell.uid), cell)

    def test_initialization_from_empty_cuds(self):
        # given
        container = Mesh('test')

        # when
        vtk_container = VTKMesh.from_mesh(container)

        # then
        self.assertEqual(vtk_container.name, container.name)
        self.assertEqual(sum(1 for _ in vtk_container.iter_points()), 0)
        self.assertEqual(sum(1 for _ in vtk_container.iter_edges()), 0)
        self.assertEqual(sum(1 for _ in vtk_container.iter_faces()), 0)
        self.assertEqual(sum(1 for _ in vtk_container.iter_cells()), 0)

    def test_initialization_from_data_set(self):
        # given
        data_set = tvtk.UnstructuredGrid()
        # set points
        data_set.points = self.points
        # set cells
        cell_array = tvtk.CellArray()
        tetra_type = tvtk.Tetra().cell_type
        hex_type = tvtk.Hexahedron().cell_type
        edge_type = tvtk.Line().cell_type
        triangle_type = tvtk.Triangle().cell_type
        cells = (
            [2] + self.edges[0] + [2] + self.edges[1] + [3] + self.faces[0] +
            [4] + self.cells[0] + [8] + self.cells[1])
        cell_types = numpy.array(
            [edge_type, edge_type, triangle_type, tetra_type, hex_type])
        offset = numpy.array([0, 3, 6, 10, 15])
        cell_array.set_cells(5, cells)
        data_set.set_cells(cell_types, offset, cell_array)
        # set point data
        index = data_set.point_data.add_array(numpy.arange(len(self.points)))
        data_set.point_data.get_array(index).name = CUBA.TEMPERATURE.name
        # set cell data
        index = data_set.cell_data.add_array(numpy.arange(len(cells)))
        data_set.cell_data.get_array(index).name = CUBA.TEMPERATURE.name

        # when
        vtk_container = VTKMesh.from_dataset('test', data_set=data_set)

        # then
        self.assertEqual(vtk_container.count_of(CUDSItem.POINT), 12)
        self.assertEqual(vtk_container.count_of(CUDSItem.EDGE), 2)
        self.assertEqual(vtk_container.count_of(CUDSItem.FACE), 1)
        self.assertEqual(vtk_container.count_of(CUDSItem.CELL), 2)
        index2point = vtk_container.index2point
        point2index = vtk_container.point2index
        for index, uid in index2point.items():
            point = vtk_container.get_point(uid)
            point.uid = None
            self.assertEqual(
                point,
                Point(
                    coordinates=self.points[index],
                    data=DataContainer(TEMPERATURE=index)))
        for edge in vtk_container.iter_edges():
            edge.uid = None
            links = [point2index[uid] for uid in edge.points]
            index = self.edges.index(links)
            self.assertEqual(
                edge,
                Edge(
                    points=[index2point[i] for i in self.edges[index]],
                    data=DataContainer(TEMPERATURE=index)))
        for face in vtk_container.iter_faces():
            face.uid = None
            self.assertEqual(
                face,
                Face(
                    points=[index2point[i] for i in self.faces[0]],
                    data=DataContainer(TEMPERATURE=2.0)))
        for cell in vtk_container.iter_cells():
            cell.uid = None
            links = [point2index[uid] for uid in cell.points]
            index = self.cells.index(links)
            self.assertEqual(
                cell,
                Cell(
                    points=[index2point[i] for i in self.cells[index]],
                    data=DataContainer(TEMPERATURE=index + 3.0)))


if __name__ == '__main__':
    unittest.main()
