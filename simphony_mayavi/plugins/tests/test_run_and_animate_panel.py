import unittest

from mayavi.core.api import NullEngine
from mayavi.sources.vtk_data_source import VTKDataSource

from pyface.ui.qt4.util.gui_test_assistant import GuiTestAssistant
from pyface.ui.qt4.util.modal_dialog_tester import ModalDialogTester

from simphony.core.cuba import CUBA

from simphony_mayavi.sources.api import EngineSource
from simphony_mayavi.plugins.run_and_animate_panel import RunAndAnimatePanel
from simphony_mayavi.tests.testing_utils import (
    is_current_backend,
    press_button_by_label,
    DummyEngine)


@unittest.skipIf(not is_current_backend("qt4"),
                 "this testcase requires backend == qt4")
class TestRunAndAnimatePanel(GuiTestAssistant, unittest.TestCase):

    def _setUp(self):
        self.engine = DummyEngine()
        self.mayavi_engine = NullEngine()

        # Add a dataset to scene
        self.engine_source = EngineSource(engine=self.engine,
                                          dataset="particles")
        self.mayavi_engine.add_source(self.engine_source)

        # RunAndAnimatePanel
        self.panel = RunAndAnimatePanel(engine=self.engine,
                                        mayavi_engine=self.mayavi_engine)

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
            press_button_by_label(ui, "Animate")

    def test_error_animate_fired_with_mayavi_engine_undefined(self):
        # given
        self.panel = RunAndAnimatePanel(engine=DummyEngine())

        # when
        def animate():
            self.panel._RunAndAnimatePanel__animate_fired()
            return True

        # then
        tester = ModalDialogTester(animate)
        tester.open_and_run(when_opened=lambda x: x.close(accept=True))
        self.assertTrue(tester.result)

    def test_error_animate_fired_with_nothing_in_scene(self):
        # given
        self.panel = RunAndAnimatePanel(engine=DummyEngine(),
                                        mayavi_engine=NullEngine())

        # when
        def animate():
            self.panel._RunAndAnimatePanel__animate_fired()
            return True

        # then
        tester = ModalDialogTester(animate)
        tester.open_and_run(when_opened=lambda x: x.close(accept=True))
        self.assertTrue(tester.result)

    def test_error_animate_fired_with_objects_not_from_current_engine(self):
        # given
        self._setUp()
        self.panel.engine = DummyEngine()
        self.panel.mayavi_engine.add_source(VTKDataSource())

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

        self.panel.engine = DummyEngine()
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
        engine_source2 = EngineSource(engine=self.engine, dataset="lattice")
        self.mayavi_engine.add_source(engine_source2)

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
        self.panel.number_of_time_steps = 999

        # then
        self.assertAlmostEqual(self.engine.CM[CUBA.TIME_STEP], 99.)
        self.assertAlmostEqual(self.engine.CM[CUBA.NUMBER_OF_TIME_STEPS], 999)

    def test_engine_parameters_update_on_engine_changed(self):
        # given
        self._setUp()

        # when
        self.panel.time_step = 99.
        self.panel.number_of_time_steps = 999
        self.panel.engine = DummyEngine()
        default_engine = DummyEngine()

        # then
        self.assertAlmostEqual(self.panel.engine.CM[CUBA.TIME_STEP],
                               default_engine.CM[CUBA.TIME_STEP])
        self.assertEqual(self.panel.engine.CM[CUBA.NUMBER_OF_TIME_STEPS],
                         default_engine.CM[CUBA.NUMBER_OF_TIME_STEPS])

    def test_error_if_time_step_not_found(self):
        engine = DummyEngine()
        mayavi_engine = NullEngine()
        engine.CM.pop(CUBA.TIME_STEP)

        # when
        def init():
            RunAndAnimatePanel(engine=engine, mayavi_engine=mayavi_engine)
            return True

        # then
        tester = ModalDialogTester(init)
        tester.open_and_run(when_opened=lambda x: x.close(accept=True))
        self.assertTrue(tester.result)

    def test_error_if_number_of_time_steps_not_found(self):
        engine = DummyEngine()
        mayavi_engine = NullEngine()
        engine.CM.pop(CUBA.NUMBER_OF_TIME_STEPS)

        # when
        def init():
            RunAndAnimatePanel(engine=engine, mayavi_engine=mayavi_engine)
            return True

        # then
        tester = ModalDialogTester(init)
        tester.open_and_run(when_opened=lambda x: x.close(accept=True))
        self.assertTrue(tester.result)
