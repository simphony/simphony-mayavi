from traits.api import Bool, Button, Int, Enum, List, Instance, Property
from traitsui.api import (View, VGroup, HGroup, Item, Action, Handler,
                          ListStrEditor, message)
from traitsui.list_str_adapter import ListStrAdapter

from simphony_mayavi.sources.api import EngineSource

from .basic_panel import BasicPanel


class EngineSourceAdapter(ListStrAdapter):
    ''' ListStrAdapter for EngineSource to be used by ListStrEditor
    for displaying info of EngineSource that is pending to be sent
    to Mayavi '''

    # The text cannot be edited
    can_edit = Bool(False)

    def _get_text(self):
        ''' Text for representing the EngineSource '''
        source = self.item
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

    def object_data_changed(self, info):
        # default point/cell scalar/vector data
        # is the first available value
        source = info.object
        if source._point_scalars_list:
            source.point_scalars_name = source._point_scalars_list[0]
        if source._point_vectors_list:
            source.point_vectors_name = source._point_vectors_list[0]
        if source._cell_scalars_list:
            source.cell_scalars_name = source._cell_scalars_list[0]
        if source._cell_vectors_list:
            source.cell_vectors_name = source._cell_vectors_list[0]

    def append_list(self, info):
        info.manager._pending_engine_sources.append(info.object)
        info.ui.dispose()


class AddSourceMixin(BasicPanel):

    # Buttons for the UI
    _add_dataset = Button("+")
    _remove_dataset = Button("-")
    _add_to_scene = Button("Add to Scene")

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
            label="Add to Mayavi"),
        title="Visualize")

    def __init__(self, engine_name, engine, visual_tool):
        ''' Initialization

        Parameters
        ----------
        engine : Instance of ABCModelingEngine
            Simphony Modeling Engine wrapper
        engine_name : str
            Name of the modeling engine
        visual_tool : mayavi.core.engine.Engine
            for visualization
        '''
        self.engine = engine
        self.engine_name = engine_name
        self.visual_tool = visual_tool
    
    # -------------------------------------------------
    # Functions relevant to the UI
    # -------------------------------------------------
    def __add_dataset_fired(self):
        source = EngineSource(self.engine_name, self.engine)
        source._dataset_changed()

        # Default trait view of EngineSource
        source_view = source.trait_view()

        # Add handler for appending to the list of pending sources
        source_view.handler = PendingEngineSourceHandler()

        # Add buttons
        AddToPending = Action(name="Confirm",
                              action="append_list")
        source_view.buttons = [AddToPending, "Cancel"]

        self.edit_traits(view=source_view,
                         context={"object": source,
                                  "manager": self})

    def __remove_dataset_fired(self):
        if len(self._pending_engine_sources) > self._pending_source_index:
            self._pending_engine_sources.pop(self._pending_source_index)

    def __add_to_scene_fired(self):
        for _ in xrange(len(self._pending_engine_sources)):
            self.add_source_to_scene(self._pending_engine_sources.pop())

    # ---------------------------------------------------
    # Public methods
    # ---------------------------------------------------

    def add_source_to_scene(self, source):
        ''' Add a source to Mayavi

        Parameters
        ----------
        source : Instance of VTKDataSource
        '''
        if self.visual_tool is None:
            text = "visual_tool is undefined"
            message(text)
            raise AttributeError(text)

        from simphony_mayavi.modules.default_module import default_module

        # add source to the current scene
        self.visual_tool.add_source(source)

        # add module to the source
        modules = default_module(source)
        for module in modules:
            self.visual_tool.add_module(module)

    def add_dataset_to_scene(self, name,
                             point_scalars_name=None, point_vectors_name=None,
                             cell_scalars_name=None, cell_vectors_name=None):
        ''' Add a dataset from the engine to Mayavi

        Parameters
        ----------
        name : str
            name of the CUDS dataset to be added
        point_scalars_name : str, optional
            CUBA name of the data to be selected as point scalars.
        point_vectors_name : str, optional
            CUBA name of the data to be selected as point vectors
        cell_scalars_name : str, optional
            CUBA name of the data to be selected as cell scalars
        cell_vectors_name : str, optional
            CUBA name of the data to be selected as cell vectors
        '''
        source = EngineSource(self.engine_name, self.engine)
        source.dataset = name
        if point_scalars_name is not None:
            source.point_scalars_name = point_scalars_name
        if point_vectors_name is not None:
            source.point_vectors_name = point_vectors_name
        if cell_scalars_name is not None:
            source.cell_scalars_name = cell_scalars_name
        if cell_vectors_name is not None:
            source.cell_vectors_name = cell_vectors_name
        self.add_source_to_scene(source)

    def show_config(self):
        self.edit_traits("panel_view", kind="live")
