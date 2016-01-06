import unittest

from simphony_mayavi.plugins.engine_manager import EngineManager
from simphony_mayavi.sources.tests import testing_utils


class TestEngineManager(unittest.TestCase):

    def test_empty_init(self):
        manager = EngineManager()

        self.assertEqual(manager.engine_name, "")
        self.assertEqual(manager.engine, None)

    def test_add_engine(self):
        engine1 = testing_utils.DummyEngine()
        engine2 = testing_utils.DummyEngine()

        manager = EngineManager()
        manager.add_engine("test", engine1)
        self.assertEqual(manager.engine_name, "test")
        self.assertEqual(manager.engine, engine1)

        manager.add_engine("test2", engine2)
        # engine is unchanged
        self.assertEqual(manager.engine_name, "test")
        self.assertEqual(manager.engine, engine1)

        self.assertIn(engine2, manager.engines.values())
        self.assertIn("test2", manager.engines.keys())

    def test_change_engine(self):
        engine1 = testing_utils.DummyEngine()
        engine2 = testing_utils.DummyEngine()

        manager = EngineManager()
        manager.add_engine("test", engine1)
        manager.add_engine("test2", engine2)

        manager.engine_name = "test2"
        self.assertEqual(manager.engine, engine2)

        manager.engine = engine1
        self.assertEqual(manager.engine_name, "test")

    def test_remove_engine(self):
        engine1 = testing_utils.DummyEngine()
        engine2 = testing_utils.DummyEngine()

        manager = EngineManager()
        manager.add_engine("test", engine1)
        manager.add_engine("test2", engine2)

        manager.remove_engine("test")
        self.assertEqual(manager.engine_name, "test2")
        self.assertEqual(manager.engine, engine2)

    def test_error_remove_last_engine(self):
        engine = testing_utils.DummyEngine()

        manager = EngineManager()
        manager.add_engine("test", engine)

        with self.assertRaises(IndexError):
            manager.remove_engine("test")

    def test_error_remove_non_existing_engine(self):
        engine = testing_utils.DummyEngine()

        manager = EngineManager()
        manager.add_engine("test", engine)

        with self.assertRaises(KeyError):
            manager.remove_engine("blah")

    def test_error_assign_foreign_engine(self):
        engine = testing_utils.DummyEngine()

        manager = EngineManager()
        manager.add_engine("test", engine)

        with self.assertRaises(ValueError):
            manager.engine = testing_utils.DummyEngine()

    def test_add_duplicate_name(self):
        engine = testing_utils.DummyEngine()

        manager = EngineManager()
        manager.add_engine("test", engine)

        with self.assertRaises(ValueError):
            manager.add_engine("test", testing_utils.DummyEngine())
