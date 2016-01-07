from pyface.api import MessageDialog
from traits.api import HasTraits, Bool, Button, Int, Enum, List, Instance, Str
from traitsui.api import (View, VGroup, HGroup, Item, Action, Handler,
                          ListStrEditor)
from traitsui.list_str_adapter import ListStrAdapter

from simphony.cuds.abc_modeling_engine import ABCModelingEngine
from simphony_mayavi.sources.api import EngineSource

from .add_engine_source_to_mayavi import add_source_and_modules_to_scene


class EngineSourceAdapter(ListStrAdapter):
    ''' ListStrAdapter for EngineSource to be used by ListStrEditor
    for displaying info of EngineSource that is pending to be sent
    to Mayavi '''

    # The displayed text cannot be edited
    can_edit = Bool(False)

    def get_text(self, object, trait, index):
        ''' Text for representing the EngineSource '''
        # All the point/cell data names being added
        source = getattr(object, trait)[index]
        data_names = ",".join([name for name in (source.point_scalars_name,
                                                 source.point_vectors_name,
                                                 source.cell_scalars_name,
                                                 source.cell_vectors_name)
                               if name])
        text = "{source}({data}) from {engine}"
        return text.format(source=source.dataset,
                           data=data_names,
                           engine=source.engine_name)


class PendingEngineSourceHandler(Handler):
    ''' UI Handler for adding dataset as a source in EngineSourceManager
    The source is appended to the ``_pending_engine_sources`` list '''

    def append_list(self, info):
        ''' Confirm and add the EngineSource to the pending list '''
        info.manager._pending_engine_sources.append(info.object)
        info.ui.dispose()


class AddSourcePanel(HasTraits):
    ''' Standalone UI for adding datasets from a modeling engine to
    a Mayavi scene

    Parameters
    ----------
    engine : Instance of ABCModelingEngine
        Simphony Modeling Engine wrapper
    engine_name : str
        Name of the modeling engine
    mayavi_engine : Instance of mayavi.core.engine.Engine
        for visualization
    '''
    engine = Instance(ABCModelingEngine)
    engine_name = Str
    mayavi_engine = Instance("mayavi.core.engine.Engine")

    label = "Add to Mayavi"

    # Buttons for the UI
    _add_dataset = Button("+")
    _remove_dataset = Button("-")
    _add_to_scene = Button("Send to Scene")

    # Pending EngineSource to be added to Mayavi
    _pending_engine_sources = List(Instance(EngineSource))

    # Selected pending EngineSource (as an index of the list)
    _pending_source = Enum(values="_pending_engine_sources")
    _pending_source_index = Int

    panel_view = View(
        VGroup(
            HGroup(
                Item("_add_dataset", show_label=False),
                Item("_remove_dataset", show_label=False,
                     enabled_when="_pending_source"),
                Item("_add_to_scene", show_label=False,
                     enabled_when="_pending_engine_sources")),
            Item("_pending_engine_sources",
                 show_label=False,
                 editor=ListStrEditor(
                     adapter=EngineSourceAdapter(),
                     editable=False,
                     selected="_pending_source",
                     selected_index="_pending_source_index")),
            ),
        title="Visualize")

    # --------------------------------------------------
    # Public methods
    # --------------------------------------------------

    def __init__(self, engine_name, engine, mayavi_engine):
        ''' Initialization

        Parameters
        ----------
        engine : Instance of ABCModelingEngine
            Simphony Modeling Engine wrapper
        engine_name : str
            Name of the modeling engine
        mayavi_engine : Instance of mayavi.core.engine.Engine
            for visualization
        '''
        self.engine = engine
        self.engine_name = engine_name
        self.mayavi_engine = mayavi_engine

    def show_config(self):
        ''' Show the GUI '''
        return self.edit_traits(view="panel_view", kind="live")

    # -------------------------------------------------
    # UI Operations
    # -------------------------------------------------

    def __add_dataset_fired(self):
        if self.engine is None:
            message_dialog = MessageDialog()
            message_dialog.error("No engine is selected")
            return

        source = EngineSource(engine=self.engine,
                              engine_name=self.engine_name)
        source._dataset_changed()

        # Default trait view of EngineSource
        source_view = source.trait_view()

        # Add handler for appending to the list of pending sources
        source_view.handler = PendingEngineSourceHandler()

        # Add buttons
        AddToPending = Action(name="Confirm",
                              action="append_list")
        source_view.buttons = [AddToPending, "Cancel"]

        return self.edit_traits(view=source_view,
                                context={"object": source,
                                         "manager": self})

    def __remove_dataset_fired(self):
        if len(self._pending_engine_sources) > self._pending_source_index:
            self._pending_engine_sources.pop(self._pending_source_index)

    def __add_to_scene_fired(self):
        added_source_indices = []   # sources that are sucessfully added
        err_messages = []   # keep all error messages for display at once

        # add source one by one
        for index, source in enumerate(self._pending_engine_sources):
            try:
                add_source_and_modules_to_scene(self.mayavi_engine, source)
            except Exception as exception:
                message_format = ("{err_type} (while adding {source}):\n"
                                  "   {message}")
                text = message_format.format(err_type=type(exception).__name__,
                                             message=exception.message,
                                             source=source.dataset)
                err_messages.append(text)
            else:
                added_source_indices.append(index)

        # Display error messages if there is any
        if len(err_messages) > 0:
            message_dialog = MessageDialog()
            message_dialog.error("\n".join(err_messages))

        # Keep the sources failed to be added
        for index in added_source_indices[::-1]:
            self._pending_engine_sources.pop(index)
