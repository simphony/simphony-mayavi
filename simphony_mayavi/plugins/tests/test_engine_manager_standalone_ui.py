import unittest

from mayavi import mlab
from mayavi.core.api import NullEngine


from simphony_mayavi.sources.tests import testing_utils
from simphony_mayavi.plugins.api import EngineManagerStandaloneUI
from simphony_mayavi.plugins.add_source_panel import AddSourcePanel
from simphony_mayavi.plugins.run_and_animate_panel import RunAndAnimatePanel


class TestEngineManagerStandaloneUI(unittest.TestCase):

    def test_init_default_mayavi_engine(self):
        # given
        engine = testing_utils.DummyEngine()
        manager = EngineManagerStandaloneUI("test", engine)

        # then
        with self.assertRaises(AttributeError):
            self.mayavi_engine

        for panel in manager.panels:
            self.assertEqual(panel.mayavi_engine, mlab.get_engine())

    def test_init_given_mayavi_engine(self):
        # given
        engine = testing_utils.DummyEngine()
        null_engine = NullEngine()
        manager = EngineManagerStandaloneUI("test", engine, null_engine)

        # then
        for panel in manager.panels:
            self.assertEqual(panel.mayavi_engine, null_engine)

    def test_init_panels(self):
        # given
        engine = testing_utils.DummyEngine()
        null_engine = NullEngine()
        manager = EngineManagerStandaloneUI("test", engine, null_engine)

        # then
        self.assertIsInstance(manager.panels.add_source, AddSourcePanel)
        self.assertIsInstance(manager.panels.run_and_animate,
                              RunAndAnimatePanel)

    def test_sync_when_engine_changed(self):
        # given
        engine1 = testing_utils.DummyEngine()
        engine2 = testing_utils.DummyEngine()
        manager = EngineManagerStandaloneUI("test", engine1, NullEngine())

        # then
        self.assertEqual(manager.panels.add_source.engine, engine1)
        self.assertEqual(manager.panels.run_and_animate.engine, engine1)

        # when
        manager.add_engine("test2", engine2)
        manager.engine = engine2

        # then
        self.assertEqual(manager.panels.add_source.engine, engine2)
        self.assertEqual(manager.panels.run_and_animate.engine, engine2)

    def test_sync_when_engine_name_changed(self):
        # given
        engine1 = testing_utils.DummyEngine()
        engine2 = testing_utils.DummyEngine()
        manager = EngineManagerStandaloneUI("test", engine1, NullEngine())
        manager.engine_name = "test"
        manager.add_engine("test2", engine2)

        # when
        manager.engine_name = "test2"

        # then
        self.assertEqual(manager.engine, engine2)
        self.assertEqual(manager.panels.add_source.engine, engine2)
        self.assertEqual(manager.panels.run_and_animate.engine, engine2)
