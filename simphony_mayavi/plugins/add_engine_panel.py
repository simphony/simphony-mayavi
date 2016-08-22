import logging

from pyface.api import MessageDialog
from traits.api import (HasTraits, Instance, List, Str, Event, Dict,
                        Bool, Property)
from traitsui.api import (View, Group, VGroup, HGroup, ButtonEditor, Item,
                          EnumEditor, TextEditor)

from simphony.cuds.abc_modeling_engine import ABCModelingEngine
from simphony_mayavi.plugins.engine_manager import EngineManager
from simphony_mayavi.plugins.engine_wrappers.api import (
    DEFAULT_ENGINE_FACTORIES, ABCEngineFactory)

logger = logging.getLogger(__name__)


class AddEnginePanel(HasTraits):
    """A panel to add a new modeling engine by creating one from
    a factory function. Then send it to the EngineManager instance
    ``engine_manager``
    """

    #: The engine manager
    engine_manager = Instance(EngineManager, allow_none=False)

    #: The new engine to be added to engine_manager
    new_engine = Instance(ABCModelingEngine)

    #: Event for UI button to call engine_manager.add_engine()
    add_engine = Event

    #: Name of the panel
    label = "Add Engine"

    #: Instantiate from a factory
    factories = Dict(Str, Instance(ABCEngineFactory))
    factory_names = List(Str)
    factory_name = Str

    #: User needs to name the engine before adding
    new_engine_name = Str

    #: Check if the name is valid
    engine_name_is_invalid = Property(Bool,
                                      depends_on="new_engine_name")

    #: Display a message if the engine_name is invalid
    status = Property(Str, depends_on="new_engine,new_engine_name")

    #: Last sanity check before the "Add engine" button is enabled
    ready_to_add = Property(Bool, depends_on="new_engine,new_engine_name")

    panel_view = View(
        VGroup(
            # Load from factory
            Group(
                Item("factory_name", show_label=False,
                     editor=EnumEditor(name="factory_names")),
                label="Create from registered engines",
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

    def _reset_create_from_factory_panel(self):
        self.factory_name = ""

    def _reset_all(self):
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

    # ------------------------------------------------------
    # Handlers for TraitsUI
    # ------------------------------------------------------

    def _factory_name_changed(self):
        ''' Use selected factory for creating a new engine
        and assign the engine to self.new_engine
        '''
        if self.factory_name:
            # engine factory selected
            factory = self.factories[self.factory_name]

            # if there is anything needs specifying, pop up a UI
            if factory.editable_traits():
                factory.configure_traits(kind="livemodal")

            # try creating the engine wrapper
            try:
                self.new_engine = factory.create()
            except Exception as exception:
                self._display_message(exception.message)
                self.new_engine = None
        else:
            self.new_engine = None

    def _get_status(self):
        ''' Message to tell the user what is wrong with the inputs'''
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
        ''' Boolean to activate the "Add Engine" button '''
        return (self.engine_manager and self.new_engine and
                not self.engine_name_is_invalid)

    def _get_engine_name_is_invalid(self):
        ''' If invalid, the TextEditor of engine_name would be red '''
        return (not self.new_engine_name or
                self.new_engine_name in self.engine_manager.engines)

    # ------------------------------------------------------
    # Default values for Traits
    # ------------------------------------------------------

    def _factories_default(self):
        return DEFAULT_ENGINE_FACTORIES

    def _factory_names_default(self):
        return [""] + self.factories.keys()
