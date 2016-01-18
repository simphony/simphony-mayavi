import logging

from pyface.api import MessageDialog
from traits.api import (HasTraits, File, Instance, List, Str, Event, Dict,
                        Bool, Property, Callable)
from traitsui.api import (View, Group, VGroup, HGroup, ButtonEditor, Item,
                          EnumEditor, TextEditor)

from simphony.cuds.abc_modeling_engine import ABCModelingEngine
from simphony_mayavi.plugins.engine_manager import EngineManager
from simphony_mayavi.plugins.engine_wrappers import loader

logger = logging.getLogger(__name__)


class AddEnginePanel(HasTraits):
    ''' A panel to load a new modeling engine from a *.py file
    or create one from a factory function.  Then send it to an
    EngineManager instance ``engine_manager``
    '''

    engine_manager = Instance(EngineManager, allow_none=False)

    # the new engine to be added to engine_manager
    new_engine = Instance(ABCModelingEngine)

    # for calling engine_manager.add_engine()
    add_engine = Event

    # Name of the panel
    label = "Add Engine"

    # Load from a python script
    # python script file
    file_name = File

    # Loaded local variables from the scripts
    # List(Str) and Str for Traits EnumEditor and listener
    loaded_variables = Dict
    loaded_variables_names = List(Str)
    selected_variable_name = Str

    # Instantiate from a factory
    factories = Dict(Str, Callable)
    factory_names = List(Str)
    factory_name = Str

    # user needs to name the engine before adding
    # it to the EngineManager
    # check if the name is valid and display a message
    new_engine_name = Str
    engine_name_is_invalid = Property(Bool,
                                      depends_on="new_engine_name")

    status = Property(Str, depends_on="new_engine,new_engine_name")
    ready_to_add = Property(Bool, depends_on="new_engine,new_engine_name")

    panel_view = View(
        VGroup(
            # Load from file
            Group(
                Item("file_name", label="File"),
                Item("selected_variable_name",
                     visible_when="loaded_variables_names",
                     label="Variable",
                     editor=EnumEditor(name="loaded_variables_names")),
                label="Load engine from *.py file",
                show_border=True),
            # Load from factory
            Group(
                Item("factory_name", show_label=False,
                     editor=EnumEditor(name="factory_names")),
                label="Create engine from factory",
                show_border=True),
            Item("new_engine_name",
                 editor=TextEditor(invalid="engine_name_is_invalid")),
            # Set a name and send it to the engine_manager
            HGroup(
                Item("add_engine",
                     show_label=False,
                     enabled_when=("ready_to_add"),
                     editor=ButtonEditor(label="Add engine")),
                Item("status",
                     style="readonly", show_label=False),
            )
        )
    )

    # --------------------------------------------------
    # UI events
    # --------------------------------------------------

    def _add_engine_fired(self):
        ''' send the new engine to the engine_manager '''
        self.engine_manager.add_engine(str(self.new_engine_name),
                                       self.new_engine)
        self._reset_all()

    def _file_name_changed(self):
        ''' Load the python script file and pull the local variables
        that are instances of ABCModelingEngine '''

        if self.file_name is None or self.file_name == "":
            return

        # Error if the file is not a *py file
        if not self.file_name.endswith(".py"):
            self._display_message("Not a *.py file")
            self._reset_load_file_panel()
            return

        # Try to exec the python file
        try:
            local_vars = self._exec_python_file(self.file_name)
        except Exception as exception:
            self._display_message(exception.message)
            self._reset_load_file_panel()
        else:
            # The python script is loaded successfully
            # only keep the local variables that are
            # instances of ABCModelingEngine
            self.loaded_variables = {name: value
                                     for name, value in local_vars.items()
                                     if isinstance(value, ABCModelingEngine)}
            self.loaded_variables_names = self.loaded_variables.keys()

            # None of the loaded local variables are ABCModelingEngine
            if len(self.loaded_variables_names) == 0:
                self._display_message("No instance of ABCModelingEngine found")
                self._reset_load_file_panel()

    def _reset_load_file_panel(self):
        self.file_name = ""
        self.loaded_variables_names = []
        self.loaded_variables = {}
        self.selected_variable_name = ""

    def _reset_create_from_factory_panel(self):
        self.factory_name = ""

    def _reset_all(self):
        self._reset_load_file_panel()
        self._reset_create_from_factory_panel()
        self.new_engine_name = ""
        self.new_engine = None

    # ---------------------------------------------------------
    # Private interfaces
    # ---------------------------------------------------------

    def _display_message(self, message, mode="error"):
        ''' Display (error) message in a dialog and send it to
        the logger '''
        message_dialog = MessageDialog()
        getattr(message_dialog, mode)(message)
        getattr(logger, mode)(message)

    def _exec_python_file(self, file_name):
        ''' Execute the python script and return only the local variables

        Returns
        -------
        local_vars : dict
        '''
        global_vars = {}
        local_vars = {}
        with open(file_name, "r") as f:
            exec(f, global_vars, local_vars)
        return local_vars

    # ------------------------------------------------------
    # Handlers for TraitsUI
    # ------------------------------------------------------

    def _factory_name_changed(self):
        if self.factory_name:
            self.new_engine = self.factories[self.factory_name]()
            self._reset_load_file_panel()
        else:
            self.new_engine = None

    def _selected_variable_name_changed(self):
        if self.selected_variable_name:
            key = self.selected_variable_name
            self.new_engine = self.loaded_variables[key]
        self._reset_create_from_factory_panel()

    # ------------------------------------------------------
    # Traits properties
    # ------------------------------------------------------

    def _get_status(self):
        if self.engine_manager is None:
            return "engine_manager is undefined"
        elif self.new_engine is None and self.new_engine_name:
            return "Please define the engine"
        elif (self.new_engine and self.new_engine_name and
              self.new_engine_name in self.engine_manager.engines):
            return "'{}' alread exists".format(self.new_engine_name)
        else:
            return ""

    def _get_ready_to_add(self):
        return (self.engine_manager and self.new_engine and
                not self.engine_name_is_invalid)

    def _get_engine_name_is_invalid(self):
        valid = (self.new_engine_name and
                 self.new_engine_name not in self.engine_manager.engines)
        return not valid

    def _factories_default(self):
        return loader.get_factories()

    def _factory_names_default(self):
        return [""] + self.factories.keys()
