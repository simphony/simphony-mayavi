import unittest

from mayavi.core.api import NullEngine

from pyface.ui.qt4.util.gui_test_assistant import GuiTestAssistant
from pyface.ui.qt4.util.modal_dialog_tester import ModalDialogTester
from traitsui.tests._tools import is_current_backend_qt4

from simphony.core.cuba import CUBA
from simphony_mayavi.sources.tests import testing_utils

from simphony_mayavi.plugins.add_engine_source_to_mayavi import (
    AddEngineSourceToMayavi)
from simphony_mayavi.plugins.run_and_animate_panel import RunAndAnimatePanel
from simphony_mayavi.plugins.tests import testing_utils as ui_test_utils


@unittest.skipIf(not is_current_backend_qt4(),
                 "this testcase requires backend == qt4")
class TestRunAndAnimatePanel(GuiTestAssistant, unittest.TestCase):

    def _setUp(self):
        self.engine = testing_utils.DummyEngine()
        self.mayavi_engine = NullEngine()

        # Add a dataset to scene
        self.add_source_handler = AddEngineSourceToMayavi(self.engine,
                                                          self.mayavi_engine)
        self.add_source_handler.add_dataset_to_scene("particles")
        self.engine_source = self.mayavi_engine.current_scene.children[0]

        # RunAndAnimatePanel
        self.panel = RunAndAnimatePanel(self.engine, self.mayavi_engine)

    def test_animate_fired(self):
        # given
        self._setUp()
        self.panel._number_of_runs = 2
        ui = self.panel.show_config()

        def engine_ran_twice(source):
            return source.engine.time >= 20.

        # animate as the engine ran for 2 times
        with self.assertTraitChangesInEventLoop(self.engine_source,
                                                "data_changed",
                                                count=2,
                                                condition=engine_ran_twice):
            ui_test_utils.press_button_by_label(ui, "Animate")

    def test_error_animate_fired_with_nothing_in_scene(self):
        # given
        self.panel = RunAndAnimatePanel(testing_utils.DummyEngine(),
                                        NullEngine())

        # when
        def animate():
            self.panel._RunAndAnimatePanel__animate_fired()
            return True

        # then
        tester = ModalDialogTester(animate)
        tester.open_and_run(when_opened=lambda x: x.close(accept=True))
        self.assertTrue(tester.result)

    def test_engine_changed(self):
        ''' Ensure that the run would stop if the engine is changed'''
        # given
        self._setUp()
        self.panel._number_of_runs = 100

        # when
        with self.event_loop_until_traits_change(self.engine_source,
                                                 "data_changed"):
            self.panel._RunAndAnimatePanel__animate_fired()

        self.panel.engine = testing_utils.DummyEngine()
        engine_time = self.engine.time

        # then
        with self.event_loop_with_timeout(repeat=1, timeout=0.6):
            # animator ui is destroyed
            animator_destroyed = (self.panel.handler._animator and
                                  self.panel.handler._animator.ui and
                                  self.panel.handler._animator.ui.destroyed)
            self.assertTrue(animator_destroyed)
            # engine time should not advance
            self.assertAlmostEqual(self.engine.time, engine_time)

    def test_update_all_scenes(self):
        # given
        self._setUp()
        engine_source1 = self.mayavi_engine.current_scene.children[0]

        self.mayavi_engine.new_scene()
        self.add_source_handler.add_dataset_to_scene("lattice", "TEMPERATURE")
        engine_source2 = self.mayavi_engine.current_scene.children[0]

        # when
        self.panel._update_all_scenes = True

        # then
        with self.assertTraitChangesInEventLoop(engine_source1, "data_changed",
                                                lambda x: x.engine.time > 5.):
            self.panel._RunAndAnimatePanel__animate_fired()
        with self.assertTraitChangesInEventLoop(engine_source2, "data_changed",
                                                lambda x: x.engine.time > 15.):
            self.panel._RunAndAnimatePanel__animate_fired()

    def test_engine_parameters_update(self):
        # given
        self._setUp()

        # when
        self.panel.time_step = 99.
        self.panel.number_of_time_steps = 999.

        # then
        self.assertAlmostEqual(self.engine.CM[CUBA.TIME_STEP], 99.)
        self.assertAlmostEqual(self.engine.CM[CUBA.NUMBER_OF_TIME_STEPS], 999.)

    def test_engine_parameters_update_on_engine_changed(self):
        # given
        self._setUp()

        # when
        self.panel.time_step = 99.
        self.panel.number_of_time_steps = 999.
        self.panel.engine = testing_utils.DummyEngine()

        # then
        self.assertAlmostEqual(self.panel.engine.CM[CUBA.TIME_STEP],
                               self.panel.time_step)
        self.assertAlmostEqual(self.panel.engine.CM[CUBA.NUMBER_OF_TIME_STEPS],
                               self.panel.number_of_time_steps)
