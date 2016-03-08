import unittest

from mock import patch

from pyface.ui.qt4.util.modal_dialog_tester import ModalDialogTester
from traits.api import Bool
from traits.testing.api import UnittestTools

from simphony.cuds.abc_modeling_engine import ABCModelingEngine
from simphony_mayavi.plugins.add_engine_panel import AddEnginePanel
from simphony_mayavi.plugins.engine_wrappers.api import ABCEngineFactory
from simphony_mayavi.plugins.engine_manager import EngineManager

from simphony_mayavi.tests.testing_utils import (
    run_and_check_dialog_was_opened,
    press_button_by_label,
    DummyEngine)


class SimpleEngineFactory(ABCEngineFactory):

    def create(self):
        return DummyEngine()


class NeedDefineEngineFactory(ABCEngineFactory):

    some_flag = Bool(True)

    def create(self):
        return DummyEngine()


class BadEngineFactory(ABCEngineFactory):

    def create(self):
        raise Exception("This is a bad engine factory")


MOCKED_ENGINE_FACTORIES = {"good_factory": SimpleEngineFactory(),
                           "need_def_factory": NeedDefineEngineFactory(),
                           "bad_factory": BadEngineFactory()}


class TestAddEnginePanel(UnittestTools, unittest.TestCase):

    @patch("simphony_mayavi.plugins.add_engine_panel.DEFAULT_ENGINE_FACTORIES",
           MOCKED_ENGINE_FACTORIES)
    def test_create_from_factory_need_more_definitions(self):
        panel = AddEnginePanel(engine_manager=EngineManager())

        def choose_factory():
            panel.factory_name = "need_def_factory"
            return True

        tester = ModalDialogTester(choose_factory)

        with self.assertTraitChanges(panel, "new_engine"):
            run_and_check_dialog_was_opened(self, tester, True)

        # ensure the new engine is defined
        self.assertIsInstance(panel.new_engine, ABCModelingEngine)

    @patch("simphony_mayavi.plugins.add_engine_panel.DEFAULT_ENGINE_FACTORIES",
           MOCKED_ENGINE_FACTORIES)
    def test_dialog_create_from_factory_with_bad_factory(self):
        panel = AddEnginePanel(engine_manager=EngineManager())

        def choose_factory():
            panel.factory_name = "bad_factory"
            return True

        tester = ModalDialogTester(choose_factory)

        # new engine would still be None
        with self.assertTraitDoesNotChange(panel, "new_engine"):
            run_and_check_dialog_was_opened(self, tester, True)

        self.assertIsNone(panel.new_engine)

    @patch("simphony_mayavi.plugins.add_engine_panel.DEFAULT_ENGINE_FACTORIES",
           MOCKED_ENGINE_FACTORIES)
    def test_create_from_factory(self):
        panel = AddEnginePanel(engine_manager=EngineManager())

        with self.assertTraitChanges(panel, "new_engine"):
            panel.factory_name = "good_factory"

        self.assertIsInstance(panel.new_engine, ABCModelingEngine)

    @patch("simphony_mayavi.plugins.add_engine_panel.DEFAULT_ENGINE_FACTORIES",
           MOCKED_ENGINE_FACTORIES)
    def test_create_from_factory_unselected(self):
        panel = AddEnginePanel(engine_manager=EngineManager())

        with self.assertTraitChanges(panel, "new_engine"):
            panel.factory_name = "good_factory"

        with self.assertTraitChanges(panel, "new_engine"):
            panel.factory_name = ""

        self.assertIs(panel.new_engine, None)

    def test_add_engine(self):
        engine_manager = EngineManager()
        panel = AddEnginePanel(engine_manager=engine_manager)
        new_engine = DummyEngine()
        panel.new_engine = new_engine
        panel.new_engine_name = "dummy"

        ui = panel.edit_traits()
        press_button_by_label(ui, "Add engine")

        # the new engine is added
        self.assertIn(new_engine, engine_manager.engines.values())
        self.assertIn("dummy", engine_manager.engines)
        # the UI should be reset
        self.assertEqual(panel.new_engine_name, "")
        self.assertIs(panel.new_engine, None)
        self.assertEqual(panel.factory_name, "")

    def test_add_engine_with_duplicated_name(self):
        # given
        engine_manager = EngineManager()
        engine_manager.add_engine("dummy", DummyEngine())

        panel = AddEnginePanel(engine_manager=engine_manager)
        panel.new_engine = DummyEngine()

        with self.assertTraitChanges(panel, "status"):
            panel.new_engine_name = "dummy"

        self.assertTrue(panel.engine_name_is_invalid)
        # not ready to add because new_engine is not defined
        self.assertFalse(panel.ready_to_add)
        # some error message is shown in the status
        self.assertNotEqual(panel.status, "")

        with self.assertTraitChanges(panel, "status"):
            panel.new_engine_name = "dummy2"

        # name is valid now
        self.assertFalse(panel.engine_name_is_invalid)
        # ready to add
        self.assertTrue(panel.ready_to_add)
        # no message shown
        self.assertEqual(panel.status, "")

    def test_not_ready_to_add_if_new_engine_undefined(self):
        # when
        panel = AddEnginePanel(engine_manager=EngineManager())
        panel.new_engine_name = "dummy"

        # name is OK
        self.assertFalse(panel.engine_name_is_invalid)
        # not ready to add because new_engine is not defined
        self.assertFalse(panel.ready_to_add)
        # some error message is shown in the status
        self.assertNotEqual(panel.status, "")

    def test_not_ready_to_add_if_new_engine_name_is_invalid(self):
        # when
        panel = AddEnginePanel(engine_manager=EngineManager())
        panel.new_engine = DummyEngine()
        panel.new_engine_name = ""

        # name is not OK
        self.assertTrue(panel.engine_name_is_invalid)
        # not ready to add
        self.assertFalse(panel.ready_to_add)
