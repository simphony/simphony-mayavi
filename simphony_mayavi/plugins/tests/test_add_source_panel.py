import unittest

from mayavi.core.api import NullEngine

from pyface.ui.qt4.util.modal_dialog_tester import ModalDialogTester
from traitsui.tests._tools import is_current_backend_qt4

from simphony_mayavi.sources.tests import testing_utils
from simphony_mayavi.plugins.add_source_panel import AddSourcePanel
from simphony_mayavi.plugins.tests import testing_utils as ui_test_utils


class TestAddSourcePanel(unittest.TestCase):

    def setUp(self):
        self.engine = testing_utils.DummyEngine()
        self.engine_name = "testing"
        self.mayavi_engine = NullEngine()
        self.panel = AddSourcePanel(self.engine_name, self.engine,
                                    self.mayavi_engine)

    def test_add_dataset(self):
        # when
        ui = self.panel._AddSourcePanel__add_dataset_fired()
        ui_test_utils.press_button_by_label(ui, "Confirm")

        self.assertEqual(len(self.panel._pending_engine_sources), 1)

    def test_remove_dataset(self):
        # given
        ui = self.panel._AddSourcePanel__add_dataset_fired()
        ui_test_utils.press_button_by_label(ui, "Confirm")

        # when
        ui = self.panel.show_config()
        ui_test_utils.press_button_by_label(ui, "-")

        # then
        self.assertEqual(len(self.panel._pending_engine_sources), 0)

    def test_add_to_scene(self):
        # given
        ui = self.panel._AddSourcePanel__add_dataset_fired()
        ui_test_utils.press_button_by_label(ui, "Confirm")

        # when
        ui = self.panel.show_config()
        ui_test_utils.press_button_by_label(ui, "Send to Scene")

        # then
        sources = self.mayavi_engine.current_scene.children
        self.assertEqual(len(sources), 1)
        self.assertEqual(sources[0].dataset, "particles")

    @unittest.skipIf(not is_current_backend_qt4(),
                     "this test requires backend==qt4")
    def test_warning_mayavi_engine_invalid(self):
        # given
        ui = self.panel._AddSourcePanel__add_dataset_fired()
        ui_test_utils.press_button_by_label(ui, "Confirm")
        ui = self.panel.show_config()

        # when
        self.panel.mayavi_engine = None

        def function():
            ui_test_utils.press_button_by_label(ui, "Send to Scene")
            return True

        # then
        # a message dialog is displayed and the pending
        tester = ModalDialogTester(function)
        tester.open_and_run(when_opened=lambda x: x.close(accept=True))
        self.assertTrue(tester.result)
        # number of EngineSource is unchanged
        self.assertEqual(len(self.panel._pending_engine_sources), 1)
