import unittest

from traits.testing.api import UnittestTools
from tvtk.api import tvtk

from simphony.cuds.particles import Particles
from simphony.cuds.mesh import Mesh
from simphony.cuds.lattice import Lattice
from simphony.cuds.abc_modeling_engine import ABCModelingEngine

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

    def test_source_name(self):
        # given
        source = EngineSource(engine=self.engine)

        # when
        source.update()

        # then
        self.assertEqual(source.name, 'Engine CUDS: particles (VTK Data (PolyData))')

        # when
        source.dataset = 'lattice'

        # then
        self.assertEqual(source.name, 'Engine CUDS: lattice (VTK Data (ImageData))')

    
