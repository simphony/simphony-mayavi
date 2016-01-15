import unittest

from traits.testing.api import UnittestTools
from tvtk.api import tvtk
from mayavi.core.api import NullEngine

from simphony.cuds.mesh import Mesh
from simphony.cuds.particles import Particles
from simphony.cuds.lattice import Lattice

from simphony_mayavi.cuds.api import VTKParticles, VTKLattice, VTKMesh
from simphony_mayavi.sources.api import EngineSource
from simphony_mayavi.sources.tests.testing_utils import DummyEngine


class TestEngineSource(unittest.TestCase, UnittestTools):
    def setUp(self):
        self.engine = DummyEngine()
        self.datasets = self.engine.get_dataset_names()

    def test_datasets(self):
        source = EngineSource(engine=self.engine)
        self.assertItemsEqual(source.datasets, self.datasets)
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
        with self.assertTraitChanges(source, 'data_changed'):
            engine.add_source(source)
        self.assertIsInstance(source.cuds, Particles)
        self.assertIsInstance(source._vtk_cuds, VTKParticles)
        self.assertIsInstance(source.outputs[0], tvtk.PolyData)
