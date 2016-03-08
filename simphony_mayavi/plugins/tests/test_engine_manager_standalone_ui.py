import unittest

from mayavi import mlab
from mayavi.core.api import NullEngine
from traits.testing.api import UnittestTools

import simphony_mayavi.tests.testing_utils
from simphony_mayavi.plugins.api import EngineManagerStandaloneUI
from simphony_mayavi.plugins.add_source_panel import AddSourcePanel
from simphony_mayavi.plugins.run_and_animate_panel import RunAndAnimatePanel


class TestEngineManagerStandaloneUI(UnittestTools, unittest.TestCase):

    def test_init_no_engine(self):
        manager = EngineManagerStandaloneUI()
        self.assertEqual(manager.engine_name, "")
        self.assertIs(manager.engine, None)
        self.assertEqual(manager.engines, {})

    def test_init_no_engine_then_add_engine(self):
        manager = EngineManagerStandaloneUI()
        engine = simphony_mayavi.tests.testing_utils.DummyEngine()
        manager.add_engine("test", engine)

        for panel in manager.panels:
            if hasattr(panel, "engine"):
                self.assertEqual(panel.engine, engine)

    def test_init_default_mayavi_engine(self):
        # given
        engine = simphony_mayavi.tests.testing_utils.DummyEngine()
        manager = EngineManagerStandaloneUI("test", engine)

        # then
        with self.assertRaises(AttributeError):
            self.mayavi_engine

        for panel in manager.panels:
            if hasattr(panel, "mayavi_engine"):
                self.assertEqual(panel.mayavi_engine, mlab.get_engine())

    def test_init_given_mayavi_engine(self):
        # given
        engine = simphony_mayavi.tests.testing_utils.DummyEngine()
        null_engine = NullEngine()
        manager = EngineManagerStandaloneUI("test", engine, null_engine)

        # then
        for panel in manager.panels:
            if hasattr(panel, "mayavi_engine"):
                self.assertEqual(panel.mayavi_engine, null_engine)

    def test_init_panels(self):
        # given
        engine = simphony_mayavi.tests.testing_utils.DummyEngine()
        null_engine = NullEngine()
        manager = EngineManagerStandaloneUI("test", engine, null_engine)

        # then
        self.assertIsInstance(manager.panels.add_source, AddSourcePanel)
        self.assertIsInstance(manager.panels.run_and_animate,
                              RunAndAnimatePanel)

    def test_sync_when_engine_changed(self):
        # given
        engine1 = simphony_mayavi.tests.testing_utils.DummyEngine()
        engine2 = simphony_mayavi.tests.testing_utils.DummyEngine()
        manager = EngineManagerStandaloneUI("test", engine1, NullEngine())

        # then
        self.assertEqual(manager.panels.add_source.engine, engine1)
        self.assertEqual(manager.panels.run_and_animate.engine, engine1)

        # when
        manager.add_engine("test2", engine2)

        # then
        with self.assertMultiTraitChanges([manager.panels.add_source,
                                           manager.panels.run_and_animate],
                                          ["engine"], []):
            manager.engine = engine2

        self.assertEqual(manager.panels.add_source.engine, engine2)
        self.assertEqual(manager.panels.run_and_animate.engine, engine2)

    def test_sync_when_engine_name_changed(self):
        # given
        engine1 = simphony_mayavi.tests.testing_utils.DummyEngine()
        engine2 = simphony_mayavi.tests.testing_utils.DummyEngine()
        manager = EngineManagerStandaloneUI("test", engine1, NullEngine())
        manager.engine_name = "test"
        manager.add_engine("test2", engine2)

        # then
        with self.assertMultiTraitChanges([manager.panels.add_source,
                                           manager.panels.run_and_animate],
                                          ["engine"], []):
            manager.engine_name = "test2"

        self.assertEqual(manager.engine, engine2)
        self.assertEqual(manager.panels.add_source.engine, engine2)
        self.assertEqual(manager.panels.run_and_animate.engine, engine2)

    def test_show_config(self):
        manager = EngineManagerStandaloneUI("test",
                                            simphony_mayavi.tests
                                            .testing_utils.DummyEngine(),
                                            NullEngine())
        manager.show_config()
