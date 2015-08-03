import unittest
import tempfile
import shutil
import os
from contextlib import closing

from tvtk.api import tvtk
from traits.testing.api import UnittestTools
from simphony.cuds.particles import Particles
from simphony.cuds.mesh import Mesh
from simphony.cuds.lattice import Lattice
from simphony.io.h5_cuds import H5CUDS
from simphony.io.h5_lattice import H5Lattice
from simphony.io.h5_mesh import H5Mesh
from simphony.io.h5_particles import H5Particles

from simphony_mayavi.sources.api import CUDSFileSource
from simphony_mayavi.cuds.api import VTKParticles, VTKLattice, VTKMesh


class TestLatticeSource(unittest.TestCase, UnittestTools):

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.maxDiff = None
        self.filename = os.path.join(self.temp_dir, 'test.cuds')
        with closing(H5CUDS.open(self.filename, mode='w')) as handle:
            handle.add_mesh(Mesh(name='mesh1'))
            handle.add_particles(Particles(name='particles1'))
            handle.add_particles(Particles(name='particles3'))
            handle.add_lattice(Lattice(
                'lattice0', 'Cubic', (0.2, 0.2, 0.2),
                (5, 10, 15), (0.0, 0.0, 0.0)))

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_initialization(self):
        source = CUDSFileSource()
        source.initialize(self.filename)
        self.assertItemsEqual(
            source.datasets, ['mesh1', 'particles1', 'particles3', 'lattice0'])
        self.assertIn(source.dataset, source.datasets)

    def test_update(self):
        source = CUDSFileSource()
        source.initialize(self.filename)

        # after initialize we need to call update to get the data loaded.
        with self.assertTraitChanges(source, 'data_changed'):
            source.update()
        self.assertIsInstance(source.cuds, H5Particles)
        self.assertIsInstance(source._vtk_cuds, VTKParticles)
        self.assertIsInstance(source.outputs[0], tvtk.PolyData)

    def test_dataset_change(self):
        source = CUDSFileSource()
        source.initialize(self.filename)

        with self.assertTraitChanges(source, 'data_changed'):
            source.dataset = 'lattice0'
        self.assertIsInstance(source.cuds, H5Lattice)
        self.assertIsInstance(source._vtk_cuds, VTKLattice)
        self.assertIsInstance(source.outputs[0], tvtk.ImageData)

        with self.assertTraitChanges(source, 'data_changed'):
            source.dataset = 'mesh1'
        self.assertIsInstance(source.cuds, H5Mesh)
        self.assertIsInstance(source._vtk_cuds, VTKMesh)
        self.assertIsInstance(source.outputs[0], tvtk.UnstructuredGrid)
