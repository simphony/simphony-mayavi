import unittest

from mayavi.core.api import NullEngine

from simphony_mayavi.plugins.add_engine_source_to_mayavi import (
    add_source_and_modules_to_scene, AddEngineSourceToMayavi)
from simphony_mayavi.sources.api import EngineSource
from simphony_mayavi.sources.tests import testing_utils


class TestAddEngineSourceToMayavi(unittest.TestCase):

    def setUp(self):
        self.engine = testing_utils.DummyEngine()
        self.engine_source = EngineSource(engine=self.engine)
        self.mayavi_engine = NullEngine()

    def test_add_source_with_point_scalars_and_vectors(self):
        # when
        self.engine_source.dataset = "particles"
        add_source_and_modules_to_scene(self.mayavi_engine,
                                        self.engine_source)

        # then
        sources = self.mayavi_engine.current_scene.children
        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0].dataset, "particles")
        modules = sources[0].children[0].children
        self.assertEqual(len(modules), 2)

    def test_add_source_with_point_scalars_only(self):
        # when
        self.engine_source.dataset = "lattice"
        add_source_and_modules_to_scene(self.mayavi_engine,
                                        self.engine_source)

        # then
        sources = self.mayavi_engine.current_scene.children
        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0].dataset, "lattice")
        modules = sources[0].children[0].children
        self.assertEqual(len(modules), 1)

    def test_exception_none_mayavi_engine(self):
        # then
        with self.assertRaises(RuntimeError):
            add_source_and_modules_to_scene(None, self.engine_source)

    def test_add_lattice_from_engine(self):
        # given
        handler = AddEngineSourceToMayavi(self.engine, self.mayavi_engine)

        # when
        handler.add_dataset_to_scene("lattice")

        # then
        sources = self.mayavi_engine.current_scene.children
        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0].dataset, "lattice")
        modules = sources[0].children[0].children
        self.assertEqual(len(modules), 1)

    def test_add_particles_from_engine(self):
        # given
        handler = AddEngineSourceToMayavi(self.engine, self.mayavi_engine)

        # when
        handler.add_dataset_to_scene("particles")

        # then
        sources = self.mayavi_engine.current_scene.children
        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0].dataset, "particles")
        modules = sources[0].children[0].children
        self.assertEqual(len(modules), 2)

    def test_add_selected_dataset_from_engine(self):
        # given
        handler = AddEngineSourceToMayavi(self.engine, self.mayavi_engine)

        # when
        handler.add_dataset_to_scene("particles", "", "VELOCITY")
        handler.add_dataset_to_scene("mesh", "", "", "TEMPERATURE", "VELOCITY")

        # then
        sources = self.mayavi_engine.current_scene.children
        self.assertEqual(len(sources), 2)
        self.assertEqual(sources[0].dataset, "particles")
        self.assertEqual(sources[0].point_scalars_name, "")
        self.assertEqual(sources[0].point_vectors_name, "VELOCITY")

        self.assertEqual(sources[1].dataset, "mesh")
        self.assertEqual(sources[1].point_scalars_name, "")
        self.assertEqual(sources[1].point_vectors_name, "")
        self.assertEqual(sources[1].cell_scalars_name, "TEMPERATURE")
        self.assertEqual(sources[1].cell_vectors_name, "VELOCITY")

        # one module for particles
        self.assertEqual(len(sources[0].children[0].children), 1)
        # two modules for mesh
        self.assertEqual(len(sources[1].children[0].children), 2)
