import unittest

from numpy import array, random
from tvtk.api import tvtk
from hypothesis import given
from hypothesis.strategies import sampled_from

from simphony.core.cuba import CUBA
from simphony.cuds.abstractmesh import ABCMesh
from simphony.cuds.abstractlattice import ABCLattice
from simphony.cuds.abstractparticles import ABCParticles
from simphony_mayavi.api import adapt2cuds


def create_unstructured_grid(array_name='scalars'):
    points = array(
        [[0, 1.2, 0.6], [1, 0, 0], [0, 1, 0], [1, 1, 1],  # tetra
         [1, 0, -0.5], [2, 0, 0], [2, 1.5, 0], [0, 1, 0],
         [1, 0, 0], [1.5, -0.2, 1], [1.6, 1, 1.5], [1, 1, 1]], 'f')  # Hex
    cells = array(
        [4, 0, 1, 2, 3,  # tetra
         8, 4, 5, 6, 7, 8, 9, 10, 11])  # hex
    offset = array([0, 5])
    tetra_type = tvtk.Tetra().cell_type  # VTK_TETRA == 10
    hex_type = tvtk.Hexahedron().cell_type  # VTK_HEXAHEDRON == 12
    cell_types = array([tetra_type, hex_type])
    cell_array = tvtk.CellArray()
    cell_array.set_cells(2, cells)
    ug = tvtk.UnstructuredGrid(points=points)
    ug.set_cells(cell_types, offset, cell_array)
    scalars = random.random(points.shape[0])
    ug.point_data.scalars = scalars
    ug.point_data.scalars.name = array_name
    scalars = random.random(cells.shape[0])
    ug.cell_data.scalars = scalars
    ug.cell_data.scalars.name = array_name
    return ug


def create_image_data(array_name='scalars'):
    data = random.random((3, 3, 3))
    i = tvtk.ImageData(spacing=(1, 1, 1), origin=(0, 0, 0))
    i.point_data.scalars = data.ravel()
    i.point_data.scalars.name = array_name
    i.dimensions = data.shape
    return i


def create_poly_data(array_name='scalars'):
    points = array([
        [0, -0.5, 0], [1.5, 0, 0], [0, 1, 0], [0, 0, 0.5],
        [-1, -1.5, 0.1], [0, -1, 0.5], [-1, -0.5, 0],
        [1, 0.8, 0]], 'f')
    lines = array([
        [0, 1, 3], [1, 2, 3], [1, 0, 5],
        [2, 3, 4], [3, 0, 4], [0, 5, 4], [2, 4, 6],
        [2, 1, 7]])
    scalars = random.random(points.shape)
    data = tvtk.PolyData(points=points, lines=lines)
    data.point_data.scalars = scalars
    data.point_data.scalars.name = array_name
    scalars = random.random(lines.shape[0])
    data.cell_data.scalars = scalars
    data.cell_data.scalars.name = array_name
    return data

good_data_sets = sampled_from([
    (create_unstructured_grid(array_name='TEMPERATURE'), 'mesh'),
    (create_image_data(array_name='TEMPERATURE'), 'lattice'),
    (create_poly_data(array_name='TEMPERATURE'), 'particles')])

bad_array_data_sets = sampled_from([
    (create_unstructured_grid(), 'mesh'),
    (create_image_data(), 'lattice'),
    (create_poly_data(), 'particles')])

auto_data_sets = sampled_from([
    (create_unstructured_grid(array_name='TEMPERATURE'), 'mesh'),
    (create_image_data(array_name='TEMPERATURE'), 'lattice'),
    (create_poly_data(array_name='TEMPERATURE'), 'particles')])

expected = {
    'mesh': ABCMesh,
    'particles': ABCParticles,
    'lattice': ABCLattice}


class TestAdapt2Cuds(unittest.TestCase):

    @given(good_data_sets)
    def test_adapt_data_set(self, setup):
        data_set, kind = setup
        container = adapt2cuds(data_set, 'test', kind)
        self.assertIsInstance(container, expected[kind])
        self.assertIs(container.data_set, data_set)

    @given(bad_array_data_sets)
    def test_adapt_data_set_with_array_rename(self, setup):
        data_set, kind = setup
        container = adapt2cuds(
            data_set, 'test', kind,
            rename_arrays={'scalars': CUBA.TEMPERATURE})
        self.assertIsInstance(container, expected[kind])
        self.assertIsNot(container.data_set, data_set)

    @given(auto_data_sets)
    def test_adapt_data_set_with_auto_detect(self, setup):
        data_set, kind = setup
        container = adapt2cuds(data_set, 'test')
        self.assertIsInstance(container, expected[kind])
        self.assertIs(container.data_set, data_set)
