import unittest
import tempfile
import shutil
import os
from contextlib import closing

from traits.testing.api import UnittestTools
from tvtk.api import tvtk
from mayavi.core.api import NullEngine
from simphony.cuds.particles import Particles
from simphony.cuds.mesh import Mesh
from simphony.cuds.lattice import make_cubic_lattice
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
            handle.add_dataset(Mesh(name='mesh1'))
            handle.add_dataset(Particles(name='particles1'))
            handle.add_dataset(Particles(name='particles3'))
            handle.add_dataset(make_cubic_lattice(
                'lattice0', 0.2, (5, 10, 15), (0.0, 0.0, 0.0)))

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

    def test_source_name(self):
        # given
        source = CUDSFileSource()
        source.initialize(self.filename)

        # when
        source.update()

        # then
        self.assertEqual(source.name, 'CUDS File: particles1 (CUDS Particles)')

        # when
        source.dataset = 'mesh1'

        # then
        self.assertEqual(source.name, 'CUDS File: mesh1 (CUDS Mesh)')

    def test_add_to_engine(self):
        source = CUDSFileSource()
        source.initialize(self.filename)
        engine = NullEngine()

        # When the source is added to an engine it should load the dataset.
        with self.assertTraitChanges(source, 'data_changed'):
            engine.add_source(source)
        self.assertIsInstance(source.cuds, H5Particles)
        self.assertIsInstance(source._vtk_cuds, VTKParticles)
        self.assertIsInstance(source.outputs[0], tvtk.PolyData)

    def test_save_load_visualization(self):
        # set up visualization
        source = CUDSFileSource()
        source.initialize(self.filename)
        engine = NullEngine()
        engine.add_source(source)

        # save the visualization
        saved_viz_file = os.path.join(self.temp_dir, 'test_saved_viz.mv2')
        engine.save_visualization(saved_viz_file)
        engine.stop()

        # restore the visualization
        engine.load_visualization(saved_viz_file)
        source_in_scene = engine.current_scene.children[0]

        # check
        self.assertItemsEqual(
            source_in_scene.datasets,
            ['mesh1', 'particles1', 'particles3', 'lattice0'])
        self.assertIn(source_in_scene.dataset,
                      source_in_scene.datasets)

    def test_error_restore_visualization_file_changed(self):
        ''' Test if the data is restored anyway for unloadable file'''
        # set up visualization
        source = CUDSFileSource()
        source.initialize(self.filename)
        engine = NullEngine()
        engine.add_source(source)

        # save the visualization
        saved_viz_file = os.path.join(self.temp_dir, 'test_saved_viz.mv2')
        engine.save_visualization(saved_viz_file)
        engine.stop()

        # now remove the file
        # the file handler to self.filename should be closed
        os.remove(self.filename)

        # restore the visualization
        engine.load_visualization(saved_viz_file)
        source_in_scene = engine.current_scene.children[0]

        # check that the data is restored anyway
        self.assertIsNotNone(source_in_scene.data)
