import unittest

from mayavi.core.api import NullEngine
from pyface.ui.qt4.util.modal_dialog_tester import ModalDialogTester
from traits.testing.api import UnittestTools

from simphony_mayavi.plugins.add_source_panel import AddSourcePanel
from simphony_mayavi.tests.testing_utils import (
    is_current_backend,
    DummyEngine,
    press_button_by_label)


class TestAddSourcePanel(UnittestTools, unittest.TestCase):

    def setUp(self):
        self.engine = DummyEngine()
        self.engine_name = "testing"
        self.mayavi_engine = NullEngine()
        self.panel = AddSourcePanel(engine_name=self.engine_name,
                                    engine=self.engine,
                                    mayavi_engine=self.mayavi_engine)

    def test_add_dataset(self):
        # when
        ui = self.panel._AddSourcePanel__add_dataset_fired()
        press_button_by_label(ui, "Confirm")

        self.assertEqual(len(self.panel._pending_engine_sources), 1)

    @unittest.skipIf(not is_current_backend("qt4"),
                     "this test requires backend==qt4")
    def test_error_add_dataset_no_engine(self):
        # when
        self.panel.engine = None

        def function():
            self.panel._AddSourcePanel__add_dataset_fired()
            return True

        # then
        # a message dialog is displayed and the pending
        tester = ModalDialogTester(function)
        tester.open_and_run(when_opened=lambda x: x.close(accept=True))
        self.assertTrue(tester.result)
        # number of EngineSource is unchanged
        self.assertEqual(len(self.panel._pending_engine_sources), 0)

    @unittest.skipIf(not is_current_backend("qt4"),
                     "this test requires backend==qt4")
    def test_error_add_dataset_when_engine_is_empty(self):
        # when
        self.engine.datasets = {}

        def function():
            self.panel._AddSourcePanel__add_dataset_fired()
            return True

        # then
        # a message dialog is displayed and the pending
        tester = ModalDialogTester(function)
        tester.open_and_run(when_opened=lambda x: x.close(accept=True))
        self.assertTrue(tester.result)
        # number of EngineSource is unchanged
        self.assertEqual(len(self.panel._pending_engine_sources), 0)

    def test_remove_dataset(self):
        # given
        ui = self.panel._AddSourcePanel__add_dataset_fired()
        press_button_by_label(ui, "Confirm")

        # when
        ui = self.panel.show_config()
        press_button_by_label(ui, "-")

        # then
        self.assertEqual(len(self.panel._pending_engine_sources), 0)

    def test_pass_remove_dataset_when_nothing_selected(self):
        ui = self.panel.show_config()
        press_button_by_label(ui, "-")

    def test_add_to_scene(self):
        # given
        ui = self.panel._AddSourcePanel__add_dataset_fired()
        press_button_by_label(ui, "Confirm")

        # when
        ui = self.panel.show_config()
        source = self.panel._pending_source

        # then
        with self.assertTraitChanges(source, "data"):
            press_button_by_label(ui, "Send to Scene")

        sources = self.mayavi_engine.current_scene.children
        self.assertEqual(len(sources), 1)
        self.assertIn(sources[0].dataset, self.engine.get_dataset_names())

    def test_pass_add_nothing_to_scene(self):
        ui = self.panel.show_config()
        press_button_by_label(ui, "Send to Scene")

    @unittest.skipIf(not is_current_backend("qt4"),
                     "this test requires backend==qt4")
    def test_warning_mayavi_engine_invalid(self):
        # given
        ui = self.panel._AddSourcePanel__add_dataset_fired()
        press_button_by_label(ui, "Confirm")
        ui = self.panel.show_config()

        # when
        self.panel.mayavi_engine = None

        def function():
            press_button_by_label(ui, "Send to Scene")
            return True

        # then
        # a message dialog is displayed and the pending
        tester = ModalDialogTester(function)
        tester.open_and_run(when_opened=lambda x: x.close(accept=True))
        self.assertTrue(tester.result)
        # number of EngineSource is unchanged
        self.assertEqual(len(self.panel._pending_engine_sources), 1)
