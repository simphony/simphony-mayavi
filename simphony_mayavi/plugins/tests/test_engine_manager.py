import unittest

from traits.testing.api import UnittestTools

import simphony_mayavi.tests.testing_utils
from simphony_mayavi.plugins.engine_manager import EngineManager


class TestEngineManager(UnittestTools, unittest.TestCase):

    def test_empty_init(self):
        manager = EngineManager()

        self.assertEqual(manager.engine_name, "")
        self.assertEqual(manager.engine, None)

    def test_add_engine(self):
        # given
        engine1 = simphony_mayavi.tests.testing_utils.DummyEngine()
        engine2 = simphony_mayavi.tests.testing_utils.DummyEngine()
        manager = EngineManager()

        # First initialisation
        with self.assertMultiTraitChanges([manager],
                                          [], ["engine", "engine_name"]):
            manager.add_engine("test", engine1)

        self.assertEqual(manager.engine_name, "test")
        self.assertEqual(manager.engine, engine1)

        # engine/engine_name are unchanged
        with self.assertMultiTraitChanges([manager],
                                          [], ["engine", "engine_name"]):
            manager.add_engine("test2", engine2)

        self.assertEqual(manager.engine_name, "test")
        self.assertEqual(manager.engine, engine1)

        self.assertIn(engine2, manager.engines.values())
        self.assertIn("test2", manager.engines.keys())

    def test_change_engine_name(self):
        engine1 = simphony_mayavi.tests.testing_utils.DummyEngine()
        engine2 = simphony_mayavi.tests.testing_utils.DummyEngine()

        manager = EngineManager()
        manager.add_engine("test", engine1)
        manager.add_engine("test2", engine2)

        # Both engine and engine_name change together
        with self.assertMultiTraitChanges([manager],
                                          ["engine", "engine_name"], []):
            manager.engine_name = "test2"
        self.assertEqual(manager.engine, engine2)

        # Both engine and engine_name change together
        with self.assertMultiTraitChanges([manager],
                                          ["engine", "engine_name"], []):
            manager.engine_name = "test"
        self.assertEqual(manager.engine, engine1)

    def test_change_engine(self):
        engine1 = simphony_mayavi.tests.testing_utils.DummyEngine()
        engine2 = simphony_mayavi.tests.testing_utils.DummyEngine()

        manager = EngineManager()
        manager.add_engine("test", engine1)
        manager.add_engine("test2", engine2)

        # Both engine and engine_name change together
        with self.assertMultiTraitChanges([manager],
                                          ["engine", "engine_name"], []):
            manager.engine = engine2

        self.assertEqual(manager.engine_name, "test2")

        # Both engine and engine_name change together
        with self.assertMultiTraitChanges([manager],
                                          ["engine", "engine_name"], []):
            manager.engine = engine1

        self.assertEqual(manager.engine_name, "test")

    def test_remove_engine_currently_selected(self):
        engine1 = simphony_mayavi.tests.testing_utils.DummyEngine()
        engine2 = simphony_mayavi.tests.testing_utils.DummyEngine()

        manager = EngineManager()
        manager.add_engine("test", engine1)
        manager.add_engine("test2", engine2)

        # Both engine and engine_name change together
        with self.assertMultiTraitChanges([manager],
                                          ["engine", "engine_name"], []):
            manager.remove_engine("test")

        self.assertEqual(manager.engine_name, "test2")
        self.assertEqual(manager.engine, engine2)

    def test_remove_engine_not_currently_selected(self):
        engine1 = simphony_mayavi.tests.testing_utils.DummyEngine()
        engine2 = simphony_mayavi.tests.testing_utils.DummyEngine()

        manager = EngineManager()
        manager.add_engine("test", engine1)
        manager.add_engine("test2", engine2)

        # Neither of engine and engine_name changes
        with self.assertMultiTraitChanges([manager],
                                          [], ["engine", "engine_name"]):
            manager.remove_engine("test2")

        self.assertEqual(manager.engine_name, "test")
        self.assertEqual(manager.engine, engine1)

    def test_error_remove_last_engine(self):
        engine = simphony_mayavi.tests.testing_utils.DummyEngine()

        manager = EngineManager()
        manager.add_engine("test", engine)

        with self.assertRaises(IndexError):
            manager.remove_engine("test")

    def test_error_remove_non_existing_engine(self):
        engine = simphony_mayavi.tests.testing_utils.DummyEngine()

        manager = EngineManager()
        manager.add_engine("test", engine)

        with self.assertRaises(KeyError):
            manager.remove_engine("blah")

    def test_error_assign_foreign_engine(self):
        engine = simphony_mayavi.tests.testing_utils.DummyEngine()

        manager = EngineManager()
        manager.add_engine("test", engine)

        with self.assertRaises(ValueError):
            manager.engine = simphony_mayavi.tests.testing_utils.DummyEngine()

    def test_add_duplicate_name(self):
        engine = simphony_mayavi.tests.testing_utils.DummyEngine()

        manager = EngineManager()
        manager.add_engine("test", engine)

        with self.assertRaises(ValueError):
            manager.add_engine("test", simphony_mayavi.tests.testing_utils
                               .DummyEngine())
