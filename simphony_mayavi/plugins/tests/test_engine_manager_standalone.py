import unittest

from mayavi import mlab
from mayavi.core.api import NullEngine
from pyface.ui.qt4.util.gui_test_assistant import GuiTestAssistant
from traitsui.tests._tools import is_current_backend_qt4

from simphony_mayavi.plugins.api import EngineManagerStandalone
from simphony_mayavi.sources.tests import testing_utils


@unittest.skipIf(not is_current_backend_qt4(),
                 "this testcase requires backend == qt4")
class TestEngineManagerStandalone(GuiTestAssistant, unittest.TestCase):

    def _setUp(self):
        self.engine = testing_utils.DummyEngine()
        self.mayavi_engine = NullEngine()
        self.manager = EngineManagerStandalone(self.engine,
                                               self.mayavi_engine)

    def test_init_default_mayavi_engine(self):
        manager = EngineManagerStandalone(testing_utils.DummyEngine())
        self.assertEqual(manager.mayavi_engine, mlab.get_engine())

    def test_add_dataset_to_scene(self):
        # given
        self._setUp()

        # when
        self.manager.add_dataset_to_scene("particles")

        # then
        sources = self.mayavi_engine.current_scene.children
        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0].dataset, "particles")
        modules = sources[0].children[0].children
        self.assertEqual(len(modules), 2)

    def test_animate(self):
        # given
        self._setUp()
        self.manager.add_dataset_to_scene("particles")
        source = self.mayavi_engine.current_scene.children[0]

        # then
        def engine_ran_twice(source):
            return source.engine.time >= 20.

        with self.assertTraitChangesInEventLoop(source, "data_changed",
                                                engine_ran_twice, count=2):
            self.manager.animate(2, delay=10)

    def test_animate_all_scenes(self):
        # given
        # scene 1
        self._setUp()
        self.manager.add_dataset_to_scene("particles")
        source1 = self.mayavi_engine.current_scene.children[0]
        # scene 2
        self.mayavi_engine.new_scene()
        self.manager.add_dataset_to_scene("particles")
        source2 = self.mayavi_engine.current_scene.children[0]

        # then
        with self.assertTraitChangesInEventLoop(source1, "data_changed",
                                                lambda x: x.engine.time > 5.):
            self.manager.animate(1, delay=10)
        with self.assertTraitChangesInEventLoop(source2, "data_changed",
                                                lambda x: x.engine.time > 15.):
            self.manager.animate(1, delay=10)

    def test_exception_animate_with_no_scene(self):
        # given
        self._setUp()

        # then
        with self.assertRaises(RuntimeError):
            self.manager.animate(2)

    def test_exception_animate_with_no_source(self):
        # given
        self._setUp()

        # when
        self.mayavi_engine.new_scene()

        # then
        with self.assertRaises(RuntimeError):
            self.manager.animate(2)

    def test_exception_animate_with_foreign_source(self):
        # given
        self._setUp()
        self.manager.add_dataset_to_scene("particles")

        # when
        self.manager.engine = testing_utils.DummyEngine()

        # then
        with self.assertRaises(RuntimeError):
            self.manager.animate(2)
