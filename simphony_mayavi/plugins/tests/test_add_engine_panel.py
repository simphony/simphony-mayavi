import os
import unittest
import tempfile
from contextlib import contextmanager

from mock import patch

from pyface.ui.qt4.util.modal_dialog_tester import ModalDialogTester
from traits.api import Bool
from traits.testing.api import UnittestTools

from simphony.cuds.abc_modeling_engine import ABCModelingEngine
from simphony_mayavi.plugins.add_engine_panel import AddEnginePanel
from simphony_mayavi.plugins.engine_wrappers.api import ABCEngineFactory
from simphony_mayavi.plugins.engine_manager import EngineManager

from simphony_mayavi.sources.tests.testing_utils import DummyEngine
from simphony_mayavi.plugins.tests.testing_utils import press_button_by_label
from simphony_mayavi.tests.testing_utils import run_and_check_dialog_was_opened


# temp_engine should be loaded successfully from this script
PYTHON_SCRIPT = '''
from simphony_mayavi.sources.tests import testing_utils

temp_engine = testing_utils.DummyEngine()
file_path = __file__
not_an_engine = 1
'''

# An error would be raised while executing this script
ERROR_PYTHON_SCRIPT = '''
from simphony_mayavi.sources.tests import testing_utils

temp_engine = testing_utils.DummyEngine()
not_an_engine =

'''

# An error would be raised for this script
# as no instance of ABCModelingEngine is found
NO_ENGINE_PYTHON_SCRIPT = '''
not_an_engine = 1
'''


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

    @contextmanager
    def write_file(self, suffix, content):
        ''' Yield the path to the temporary file

        Parameters
        ----------
        suffix : str
            suffix of the file
        content : str
            content of the file to be written
        '''
        # create a python script file
        file_d, tmp_path = tempfile.mkstemp(suffix=suffix)

        try:
            # write the sample script
            with open(tmp_path, "w") as tmpfile:
                tmpfile.write(content)
        except IOError:
            message = "Cannot create temporary script file for testing"
            raise IOError(message)
        else:
            yield tmp_path
        finally:
            # remove the temporary file
            os.remove(tmp_path)

    def test_load_engine_from_file(self):
        panel = AddEnginePanel(engine_manager=EngineManager())

        with self.write_file(".py", PYTHON_SCRIPT) as tmp_path:
            with self.assertMultiTraitChanges([panel],
                                              ["file_name",
                                               "loaded_variables_names"], []):
                panel.file_name = tmp_path
            with self.assertTraitChanges(panel, "new_engine"):
                panel.selected_variable_name = "temp_engine"

        # only the local variable that is an instance of
        # ABCModelingEngine is loaded
        self.assertIn("temp_engine", panel.loaded_variables_names)
        self.assertNotIn("not_an_engine", panel.loaded_variables_names)

    def test_error_load_engine_from_error_file(self):
        panel = AddEnginePanel(engine_manager=EngineManager())

        def set_file_name():
            panel.file_name = tmp_path
            return True

        # for testing modal dialog
        tester = ModalDialogTester(set_file_name)

        # The content of the script leads to error during ``exec``
        with self.write_file(".py", ERROR_PYTHON_SCRIPT) as tmp_path:
            run_and_check_dialog_was_opened(self, tester, True)

    def test_error_load_from_non_py_file(self):
        panel = AddEnginePanel(engine_manager=EngineManager())

        def set_file_name():
            panel.file_name = tmp_path
            return True

        # for testing modal dialog
        tester = ModalDialogTester(set_file_name)

        # The file does not end with *.py
        with self.write_file("", PYTHON_SCRIPT) as tmp_path:
            run_and_check_dialog_was_opened(self, tester, True)

    def test_error_load_from_py_file_no_engine(self):
        panel = AddEnginePanel(engine_manager=EngineManager())

        def set_file_name():
            panel.file_name = tmp_path
            return True

        # for testing modal dialog
        tester = ModalDialogTester(set_file_name)

        # The script contains no local variable that is an instance
        # of ABCModelingEngine
        with self.write_file(".py", NO_ENGINE_PYTHON_SCRIPT) as tmp_path:
            run_and_check_dialog_was_opened(self, tester, True)

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

        # ensure the load-from-file panel is reset
        self.assertEqual(panel.file_name, "")
        self.assertTrue(len(panel.loaded_variables_names) == 0)

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

        # ensure the load-from-file panel is reset
        self.assertEqual(panel.file_name, "")
        self.assertTrue(len(panel.loaded_variables_names) == 0)

    @patch("simphony_mayavi.plugins.add_engine_panel.DEFAULT_ENGINE_FACTORIES",
           MOCKED_ENGINE_FACTORIES)
    def test_create_from_factory(self):
        panel = AddEnginePanel(engine_manager=EngineManager())

        with self.assertTraitChanges(panel, "new_engine"):
            panel.factory_name = "good_factory"

        self.assertIsInstance(panel.new_engine, ABCModelingEngine)
        self.assertEqual(panel.file_name, "")
        self.assertTrue(len(panel.loaded_variables_names) == 0)

    @patch("simphony_mayavi.plugins.add_engine_panel.DEFAULT_ENGINE_FACTORIES",
           MOCKED_ENGINE_FACTORIES)
    def test_factory_section_reset_after_load_from_file(self):
        panel = AddEnginePanel(engine_manager=EngineManager())
        panel.factory_name = "good_factory"

        with self.write_file(".py", PYTHON_SCRIPT) as tmp_path:

            # only defined the file
            with self.assertTraitDoesNotChange(panel, "factory_name"):
                panel.file_name = tmp_path

            # now select the local variable loaded
            with self.assertMultiTraitChanges([panel],
                                              ["factory_name", "new_engine"],
                                              []):
                selected_variable_name = panel.loaded_variables_names[-1]
                panel.selected_variable_name = selected_variable_name

        # new_engine should be defined
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

        # The load-from-file section should be reset
        self.assertEqual(panel.file_name, "")
        self.assertEqual(len(panel.loaded_variables_names), 0)
        self.assertEqual(panel.loaded_variables, {})
        self.assertEqual(panel.selected_variable_name, "")

    @patch("simphony_mayavi.plugins.add_engine_panel.DEFAULT_ENGINE_FACTORIES",
           MOCKED_ENGINE_FACTORIES)
    def test_reset_factory_section_when_loaded_from_file(self):
        panel = AddEnginePanel(engine_manager=EngineManager())

        with self.assertTraitChanges(panel, "new_engine"):
            panel.factory_name = "good_factory"

        with self.write_file(".py", PYTHON_SCRIPT) as tmp_path:
            panel.file_name = tmp_path
            panel.selected_variable_name = panel.loaded_variables_names[-1]

        self.assertIsInstance(panel.new_engine, ABCModelingEngine)
        # create-from-factory section should be reset
        self.assertEqual(panel.factory_name, "")

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
        self.assertEqual(panel.loaded_variables, {})
        self.assertEqual(panel.selected_variable_name, "")
        self.assertEqual(panel.file_name, "")
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
