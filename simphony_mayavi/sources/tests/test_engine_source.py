import unittest
import shutil
import os
import tempfile

from traits.testing.api import UnittestTools
from tvtk.api import tvtk
from mayavi.core.api import NullEngine

from simphony.cuds.mesh import Mesh
from simphony.cuds.particles import Particles
from simphony.cuds.lattice import Lattice

from simphony_mayavi.cuds.api import VTKParticles, VTKLattice, VTKMesh
from simphony_mayavi.sources.api import EngineSource
from simphony_mayavi.tests.testing_utils import DummyEngine


class TestEngineSource(unittest.TestCase, UnittestTools):
    def setUp(self):
        self.engine = DummyEngine()
        self.datasets = self.engine.get_dataset_names()

        # for testing save/load visualization
        self.temp_dir = tempfile.mkdtemp()

    def tearDown(self):
        shutil.rmtree(self.temp_dir)

    def test_datasets(self):
        source = EngineSource(engine=self.engine)
        self.assertSequenceEqual(set(source.datasets), set(self.datasets))
        self.assertIn(source.dataset, source.datasets)

    def test_update(self):
        source = EngineSource(engine=self.engine)

        with self.assertTraitChanges(source, "data_changed"):
            source.dataset = "particles"
        self.assertIsInstance(source.cuds, Particles)
        self.assertIsInstance(source._vtk_cuds, VTKParticles)
        self.assertIsInstance(source.outputs[0], tvtk.PolyData)

        with self.assertTraitChanges(source, "data_changed"):
            source.dataset = "lattice"
        self.assertIsInstance(source.cuds, Lattice)
        self.assertIsInstance(source._vtk_cuds, VTKLattice)
        self.assertIsInstance(source.outputs[0], tvtk.ImageData)

        with self.assertTraitChanges(source, "data_changed"):
            source.dataset = "mesh"
        self.assertIsInstance(source.cuds, Mesh)
        self.assertIsInstance(source._vtk_cuds, VTKMesh)
        self.assertIsInstance(source.outputs[0], tvtk.UnstructuredGrid)

    def test_initialization(self):
        source = EngineSource(engine=self.engine)
        # cuds is not yet obtained from the engine on init
        self.assertIs(source._cuds, None)
        self.assertIs(source._vtk_cuds, None)

    def test_init_with_engine_and_dataset(self):
        """ Test if engine and dataset can be defined on init.
        Since the dataset is defined, vtk_data should be loaded
        """
        # when
        source = EngineSource(engine=self.engine, dataset="lattice")

        # then
        self.assertEqual(source.engine, self.engine)
        self.assertEqual(source.dataset, "lattice")
        self.assertIsInstance(source._cuds, Lattice)
        self.assertIsInstance(source._vtk_cuds, VTKLattice)

    def test_init_with_engine_and_data_attributes(self):
        """ Test if engine, point_scalars can be defined on init.
        Note that dataset is assumed to be the first available
        """
        # when
        source = EngineSource(engine=self.engine,
                              point_scalars="TEMPERATURE")

        # then
        self.assertEqual(source.engine, self.engine)
        self.assertIn(source.dataset, self.datasets)
        self.assertEqual(source.point_scalars_name, "TEMPERATURE")

    def test_init_with_engine_and_dataset_and_data_attributes(self):
        """ Test if engine, dataset and data attributes can be defined on init.
        """
        # when
        source = EngineSource(engine=self.engine, dataset="mesh",
                              cell_scalars="TEMPERATURE",
                              cell_vectors="VELOCITY")

        # then
        self.assertEqual(source.engine, self.engine)
        self.assertEqual(source.dataset, "mesh")
        self.assertIsInstance(source._cuds, Mesh)
        self.assertIsInstance(source._vtk_cuds, VTKMesh)

        # These are the one defined
        self.assertEqual(source.cell_scalars_name, "TEMPERATURE")
        self.assertEqual(source.cell_vectors_name, "VELOCITY")

        # This is assumed (i.e. first available)
        self.assertEqual(source.point_scalars_name, "TEMPERATURE")

    def test_source_name(self):
        # given
        source = EngineSource(engine=self.engine)

        # when
        source.dataset = "particles"

        # then
        self.assertEqual(source.name, "particles (CUDS from engine)")

        # when
        source.dataset = "mesh"

        # then
        self.assertEqual(source.name, "mesh (CUDS from engine)")

        # when
        source.dataset = 'lattice'

        # then
        self.assertEqual(source.name, "lattice (CUDS from engine)")

    def test_add_to_engine(self):
        source = EngineSource(engine=self.engine)
        engine = NullEngine()

        # When the source is added to an engine it should load the dataset.
        # Since the dataset is not defined during initialisation,
        # one of the available datasets is randomly selected
        with self.assertTraitChanges(source, 'data_changed'):
            engine.add_source(source)

        self.assertIsInstance(source.cuds,
                              (Particles, Lattice, Mesh))
        self.assertIsInstance(source._vtk_cuds,
                              (VTKParticles, VTKLattice, VTKMesh))
        self.assertIsInstance(source.outputs[0],
                              (tvtk.PolyData, tvtk.ImageData,
                               tvtk.UnstructuredGrid))

    def test_save_load_visualization(self):
        # set up the visualization
        source = EngineSource(engine=self.engine)
        source.dataset = "particles"   # data changed
        engine = NullEngine()
        engine.add_source(source)

        # save the visualization
        saved_viz_file = os.path.join(self.temp_dir, 'test_saved_viz.mv2')
        engine.save_visualization(saved_viz_file)
        engine.stop()

        # restore the visualization
        engine.load_visualization(saved_viz_file)

        # then
        source_in_scene = engine.current_scene.children[0]

        # data is restored
        self.assertIsNotNone(source_in_scene.data)
        self.assertEqual(source_in_scene.dataset, "particles")
        self.assertSequenceEqual(source_in_scene.datasets, ["particles"])
        self.assertEqual(source_in_scene.name, source.name)

        # But engine, cuds and vtk_cuds are not available
        self.assertIsNone(source_in_scene.engine)
        self.assertIsNone(source_in_scene._vtk_cuds)
        self.assertIsNone(source_in_scene._cuds)

        # when engine is assigned, cuds should be updated
        with self.assertTraitChanges(source_in_scene, "cuds"):
            source_in_scene.engine = self.engine
