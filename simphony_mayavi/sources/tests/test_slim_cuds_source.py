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
from simphony_mayavi.sources.api import CUDSSource
from simphony_mayavi.sources.slim_cuds_source import SlimCUDSSource, \
    _available_keys


class TestParticlesSource(unittest.TestCase):
    def setUp(self):
        self.points = [
            [0.0, 0.0, 0.0], [1.0, 0.0, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]]
        self.bonds = [[0, 1], [0, 3], [1, 3, 2]]
        self.point_temperature = [10., 20., 30., 40.]
        self.point_radius = [1., 2., 3., 4.]
        self.point_mass = [4., 8., 16., 32.]
        self.bond_temperature = [60., 80., 190., 5.]

        self.cuds = Particles('test')

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

        self.point_uids = self.cuds.add_particles(particle_iter())

        # add bonds
        def bond_iter():
            for temp, indices in zip(self.bond_temperature, self.bonds):
                yield Bond(particles=[self.point_uids[index]
                                      for index in indices],
                           data=DataContainer(
                               TEMPERATURE=temp,
                               ))

        self.bond_uids = self.cuds.add_bonds(bond_iter())

        # for testing save/load visualization
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_particles(self):
        cuds = self.cuds

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
            point = self.cuds.get_particle(key)
            assert_array_equal(points[index], point.coordinates)
            self.assertEqual(temperature[index], point.data[CUBA.TEMPERATURE])

        source.point_scalars_name = "MASS"
        self.assertEqual(dataset.point_data.number_of_arrays, 1)
        dataset = source.data
        mass = dataset.point_data.get_array('MASS')
        for key, index in vtk_cuds.particle2index.iteritems():
            point = self.cuds.get_particle(key)
            assert_array_equal(points[index], point.coordinates)
            self.assertEqual(mass[index], point.data[CUBA.MASS])

        source.point_scalars_name = ""
        dataset = source.data
        self.assertEqual(dataset.point_data.number_of_arrays, 0)

    def test_available_keys(self):
        (point_scalars,
         point_vectors,
         cell_scalars,
         cell_vectors) = _available_keys(self.cuds)

        self.assertEqual(point_scalars, {CUBA.TEMPERATURE,
                                         CUBA.RADIUS,
                                         CUBA.MASS})

        self.assertEqual(point_vectors, set())
        self.assertEqual(cell_scalars, {CUBA.TEMPERATURE})
        self.assertEqual(cell_vectors, set())

    def test_bonds(self):
        source = SlimCUDSSource(cuds=self.cuds)

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
            bond = self.cuds.get_bond(key)
            particles = [
                vtk_cuds.particle2index[uid] for uid in bond.particles]
            self.assertEqual(bonds[index], particles)
            self.assertEqual(temperature[index], bond.data[CUBA.TEMPERATURE])

        # Clearing should empty the data again
        source.cell_scalars_name = ""
        dataset = source.data
        self.assertEqual(dataset.cell_data.number_of_arrays, 0)
