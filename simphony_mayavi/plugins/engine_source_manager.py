from __future__ import print_function

import logging

from simphony.core.cuba import CUBA
from simphony.cuds.abc_modeling_engine import ABCModelingEngine
from simphony_mayavi.sources.api import EngineSource
from traits.api import (HasTraits, Instance, ListStr, Button, Str, Float, Int,
                        Bool, List, Dict, Property, Enum, Any)
from traitsui.api import (View, Group, VGroup, HGroup, Item, message, Include,
                          Action, Handler, TabularEditor, ListStrEditor)
from traitsui.tabular_adapter import TabularAdapter
from traitsui.list_str_adapter import ListStrAdapter

from mayavi.core.trait_defs import DEnum

# This class is intended to be used as a standalone as well as an evisage
# plugin for mayavi.  For the latter, mayavi imports cannot be put at the
# module level or it would cause import cycles


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


class AddSourcePanel(HasTraits):

    engine = Instance(ABCModelingEngine)
    engine_name = Str
    mayavi_engine = Any

    # ----------------------------------------------
    # For adding sources to scences
    # (Only relevant to UI)
    # ----------------------------------------------
    _add_dataset = Button("+")
    _remove_dataset = Button("-")
    _add_to_scene = Button("Add to Scene")

    # Pending EngineSource to be added to Mayavi
    _pending_engine_sources = List(Instance(EngineSource))
    
    # Selected pending EngineSource (as an index of the list)
    _pending_source = Enum(values="_pending_engine_sources")
    _pending_source_index = Int

    trait_view = View(Include("panel_view"))

    panel_view = VGroup(
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
        label="Add Source(s)")

    # ------------------------------------------------
    # Read only attributes (delayed evaluations)
    # ------------------------------------------------
    @property
    def datasets(self):
        """ Datasets (list) in the modeling engines """
        return self.engine.get_dataset_names()

    # -------------------------------------------------
    # Functions relevant to the UI
    # -------------------------------------------------
    def __add_dataset_fired(self):
        source = EngineSource(self.engine_name, self.engine)

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
        self._pending_engine_sources.pop(self._pending_source_index)

    def __add_to_scene_fired(self):
        for _ in xrange(len(self._pending_engine_sources)):
            self.add_source_to_scene(self._pending_engine_sources.pop())

    # ---------------------------------------------------
    # Public methods
    # ---------------------------------------------------

    def add_source_to_scene(self, source):
        from simphony_mayavi.modules.default_module import default_module

        # add source to the current scene
        self.mayavi_engine.add_source(source)

        # add module to the source
        modules = default_module(source)
        for module in modules:
            self.mayavi_engine.add_module(module)

    def add_dataset_to_scene(self, name,
                             point_scalars_name="", point_vectors_name="",
                             cell_scalars_name="", cell_vectors_name=""):
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
        if point_scalars_name:
            source.point_scalars_name = point_scalars_name
        if point_vectors_name:
            source.point_vectors_name = point_vectors_name
        if cell_scalars_name:
            source.cell_scalars_name = cell_scalars_name
        if cell_vectors_name:
            source.cell_vectors_name = cell_vectors_name
        self.add_source_to_scene(source)


class RunAndAnimatePanel(HasTraits):

    engine = Instance(ABCModelingEngine)
    mayavi_engine = Any

    # -------------------------------------------------------
    # Basic time step parameters to interact with the engine
    # -------------------------------------------------------
    time_step = Float(allow_none=False)
    number_of_time_steps = Float(allow_none=False)

    # ----------------------------------------------
    # For running the engine and animating scenes
    # (Only relevant to UI)
    # ----------------------------------------------
    _number_of_runs = Int(1)
    _animate = Button("Animate")
    _animator = None
    _animate_delay = 20
    _update_all_scenes = Bool(False)
    
    trait_view = View(Include("panel_view"))
    
    panel_view = VGroup(
        Item("time_step"),
        Item("number_of_time_steps"),
        HGroup(Item(name="_number_of_runs", label="Runs for"),
               Item(label="time(s)")),
        HGroup(Item("_animate", show_label=False),
               Item(name="_update_all_scenes", label="Update all scenes")),
        label="Run/Animate")

    def __animate_fired(self):
        self.animate(self._number_of_runs,
                     update_all_scenes=self._update_all_scenes)

    # ----------------------------------------------------------
    # Trait handlers
    # ----------------------------------------------------------

    def _time_step_changed(self):
        self.engine.CM[CUBA.TIME_STEP] = self.time_step

    def _number_of_time_steps_changed(self):
        value = self.number_of_time_steps
        self.engine.CM[CUBA.NUMBER_OF_TIME_STEPS] = value

    def _engine_changed(self):
        self._setup_run_parameters()

    def animate(self, number_of_runs, delay=None, ui=True,
                update_all_scenes=False):
        ''' Run the modeling engine, update and thus animate the scene
        at the end of each run

        Parameters
        ----------
        number_of_runs : int
           the number of times the engine.run() is called
        delay : int
           delay between each run.
           If None, use last setting or Mayavi's default: 500
        ui : bool
           whether an UI is shown
        update_all_scenes : bool
           whether all scenes are updated
        '''
        from mayavi.mlab import animate

        # remember the last delay being set
        if delay is None:
            if self._animator:
                delay = self._animator.delay
            else:
                delay = 500

        # close the old window and start a new one
        # FIXME: there should be a better way
        if self._animator and not self._animator.ui.destroyed:
            self._animator.close()

        if update_all_scenes:
            get_sources_func = self.get_all_sources
        else:
            get_sources_func = self.get_current_sources

        try:
            sources = get_sources_func()
        except AttributeError:
            text = "Nothing in scene.  Engine is not run."
            message(text)
            raise RuntimeError(text)

        @animate(delay=delay, ui=ui)
        def anim():
            for _ in xrange(number_of_runs):
                self.engine.run()
                self.update_sources(sources)
                self.mayavi_engine.current_scene.render()
                yield()
        self._animator = anim()

    def update_sources(self, sources):
        ''' Update multiple sources'''
        for source in sources:
            source.update()

    def get_current_sources(self):
        ''' Return the current scene's sources that are belong
        to this manager's modeling engine

        Returns
        -------
        sources : set of EngineSource
        '''
        sources = self.mayavi_engine.current_scene.children
        return {source for source in sources
                if source.engine == self.engine}

    def get_all_sources(self):
        ''' Return sources from all the scenes and that the sources
        are belong to this manager's modeling engine

        Returns
        -------
        sources : set of EngineSource
        '''
        sources = {source
                   for scene in self.mayavi_engine.scenes
                   for source in scene.children
                   if source.engine == self.engine}
        return sources

    # ---------------------------------------------------------
    # Private methods
    # ---------------------------------------------------------
    def _setup_run_parameters(self):
        CM = self.engine.CM

        # For interacting with the engine
        if CUBA.TIME_STEP in CM:
            self.time_step = CM[CUBA.TIME_STEP]
        else:
            logging.warning("TIME_STEP is not found.")

        if CUBA.NUMBER_OF_TIME_STEPS in CM:
            value = CM[CUBA.NUMBER_OF_TIME_STEPS]
            self.number_of_time_steps = value
        else:
            logging.warning("NUMBER_OF_TIME_STEPS is not found.")


        
class EngineSourceManager(HasTraits):
    ''' A basic tool for visualising CUDS datasets from a modeling
    engine as well as performing basic operations on the engine

    Examples
    ---------
    >>> from simphony.engine import lammps   # LAMMPS
    >>> # Setup the engine so it is ready to run
    >>> dem = lammps.LammpsWrapper(...)
    >>> # Setup for visualization
    >>> from simphony_mayavi.plugins.api import EngineSourceManager
    >>> manager = EngineSourceManager("test", dem)
    >>> manager.show_config()   # GUI

    One can still perform all functions of this manager without
    opening up a GUI ::

    >>> from simphony_mayavi.plugins.api import EngineSourceManager
    >>> manager = EngineSourceManager("test", dem)
    >>> manager.datasets   # display all available datasets
    ["particles1", "mesh1"]
    >>> # Show the particles1 CUDS
    >>> manager.add_dataset_to_scene("particles")
    >>> # Run the engine 10 times and animate the results
    >>> manager.animate(10)
    >>> # Adjust time step of the engine
    >>> manager.time_step = 0.1
    >>> # Adjust the number of time steps for each run
    >>> manager.number_of_time_steps = 100
    '''
    # Set by Envisage when this class is used as a mayavi plugin
    window = Instance("pyface.workbench.api.WorkbenchWindow")

    # Engines that are added to the manager
    engines = Dict(Str, Instance(ABCModelingEngine))

    # Names of engines in the Manager
    _engine_names = ListStr

    # Selected engine name
    # DEnum is used so that the dropdown menu is automatically updated
    # when new engine is added
    engine_name = DEnum(values_name="_engine_names")

    # -------------------------------------------------------
    # Basic time step parameters to interact with the engine
    # -------------------------------------------------------
    time_step = Float(allow_none=False)
    number_of_time_steps = Float(allow_none=False)

    # ----------------------------------------------
    # For adding sources to scences
    # (Only relevant to UI)
    # ----------------------------------------------
    _add_dataset = Button("+")
    _remove_dataset = Button("-")
    _add_to_scene = Button("Add to Scene")

    # Pending EngineSource to be added to Mayavi
    _pending_engine_sources = List(Instance(EngineSource))
    
    # Selected pending EngineSource (as an index of the list)
    _pending_source = Enum(values="_pending_engine_sources")
    _pending_source_index = Int

    # ----------------------------------------------
    # For running the engine and animating scenes
    # (Only relevant to UI)
    # ----------------------------------------------
    _number_of_runs = Int(1)
    _animate = Button("Animate")
    _animator = None
    _animate_delay = 20
    _update_all_scenes = Bool(False)

    traits_view = View(
        Item("engine_name", label="Engine Wrapper"),
        VGroup(Include("dataset_view"),
               Include("animate_view"),
               layout="tabbed"),
        resizable=True)

    dataset_view = VGroup(
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
        label="Add Source(s)")

    animate_view = VGroup(
        Item("time_step"),
        Item("number_of_time_steps"),
        HGroup(Item(name="_number_of_runs", label="Runs for"),
               Item(label="time(s)")),
        HGroup(Item("_animate", show_label=False),
               Item(name="_update_all_scenes", label="Update all scenes")),
        label="Run/Animate")

    # ------------------------------------------------
    # Read only attributes (delayed evaluations)
    # ------------------------------------------------
    @property
    def datasets(self):
        """ Datasets (list) in the modeling engines """
        return self.current_engine.get_dataset_names()

    @property
    def current_engine(self):
        return self.engines[self.engine_name]

    # ----------------------------------------------------
    # Initialization
    # ----------------------------------------------------
    def __init__(self, name, modeling_engine, as_plugin=False):
        # SimPhoNy Modeling Engine wrapper
        self.add_engine(name, modeling_engine)

        if as_plugin:
            # as Mayavi plugin
            from mayavi.plugins.script import Script
            self.mayavi_engine = self.window.get_service(Script)
        else:
            # default standalone
            from mayavi import mlab
            self.mayavi_engine = mlab.get_engine()

    # -------------------------------------------------
    # Functions relevant to the UI
    # -------------------------------------------------
    def __add_dataset_fired(self):
        source = EngineSource(self.engine_name, self.current_engine)

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
        self._pending_engine_sources.pop(self._pending_source_index)

    def __add_to_scene_fired(self):
        for _ in xrange(len(self._pending_engine_sources)):
            self.add_source_to_scene(self._pending_engine_sources.pop())

    def __animate_fired(self):
        self.animate(self._number_of_runs,
                     update_all_scenes=self._update_all_scenes)

    # ----------------------------------------------------------
    # Trait handlers
    # ----------------------------------------------------------

    def _time_step_changed(self):
        self.current_engine.CM[CUBA.TIME_STEP] = self.time_step

    def _number_of_time_steps_changed(self):
        value = self.number_of_time_steps
        self.current_engine.CM[CUBA.NUMBER_OF_TIME_STEPS] = value

    def _engine_name_changed(self):
        self._setup_run_parameters()

    # -----------------------------------------------------------
    # Public methods
    # -----------------------------------------------------------

    def add_engine(self, name, modeling_engine):
        self.engines[name] = modeling_engine
        self._engine_names = self.engines.keys()
        self.engine_name = name

    def animate(self, number_of_runs, delay=None, ui=True,
                update_all_scenes=False):
        ''' Run the modeling engine, update and thus animate the scene
        at the end of each run

        Parameters
        ----------
        number_of_runs : int
           the number of times the engine.run() is called
        delay : int
           delay between each run.
           If None, use last setting or Mayavi's default: 500
        ui : bool
           whether an UI is shown
        update_all_scenes : bool
           whether all scenes are updated
        '''
        from mayavi.mlab import animate

        # remember the last delay being set
        if delay is None:
            if self._animator:
                delay = self._animator.delay
            else:
                delay = 500

        # close the old window and start a new one
        # FIXME: there should be a better way
        if self._animator and not self._animator.ui.destroyed:
            self._animator.close()

        if update_all_scenes:
            get_sources_func = self.get_all_sources
        else:
            get_sources_func = self.get_current_sources

        try:
            sources = get_sources_func()
        except AttributeError:
            text = "Nothing in scene.  Engine is not run."
            message(text)
            raise RuntimeError(text)

        @animate(delay=delay, ui=ui)
        def anim():
            for _ in xrange(number_of_runs):
                self.current_engine.run()
                self.update_sources(sources)
                self.mayavi_engine.current_scene.render()
                yield()
        self._animator = anim()

    def update_sources(self, sources):
        ''' Update multiple sources'''
        for source in sources:
            source.update()

    def add_source_to_scene(self, source):
        from simphony_mayavi.modules.default_module import default_module

        # add source to the current scene
        self.mayavi_engine.add_source(source)

        # add module to the source
        modules = default_module(source)
        for module in modules:
            self.mayavi_engine.add_module(module)

    def add_dataset_to_scene(self, name,
                             point_scalars_name="", point_vectors_name="",
                             cell_scalars_name="", cell_vectors_name=""):
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
        source = EngineSource(self.engine_name, self.current_engine)
        source.dataset = name
        if point_scalars_name:
            source.point_scalars_name = point_scalars_name
        if point_vectors_name:
            source.point_vectors_name = point_vectors_name
        if cell_scalars_name:
            source.cell_scalars_name = cell_scalars_name
        if cell_vectors_name:
            source.cell_vectors_name = cell_vectors_name
        self.add_source_to_scene(source)

    def get_current_sources(self):
        ''' Return the current scene's sources that are belong
        to this manager's modeling engine

        Returns
        -------
        sources : set of EngineSource
        '''
        sources = self.mayavi_engine.current_scene.children
        return {source for source in sources
                if source.engine == self.current_engine}

    def get_all_sources(self):
        ''' Return sources from all the scenes and that the sources
        are belong to this manager's modeling engine

        Returns
        -------
        sources : set of EngineSource
        '''
        sources = {source
                   for scene in self.mayavi_engine.scenes
                   for source in scene.children
                   if source.engine == self.current_engine}
        return sources

    def show_config(self):
        ''' Show the UI of this manager
        '''
        self.configure_traits(kind="live")

    # ---------------------------------------------------------
    # Private methods
    # ---------------------------------------------------------
    def _setup_run_parameters(self):
        CM = self.current_engine.CM

        # For interacting with the engine
        if CUBA.TIME_STEP in CM:
            self.time_step = CM[CUBA.TIME_STEP]
        else:
            logging.warning("TIME_STEP is not found.")

        if CUBA.NUMBER_OF_TIME_STEPS in CM:
            value = CM[CUBA.NUMBER_OF_TIME_STEPS]
            self.number_of_time_steps = value
        else:
            logging.warning("NUMBER_OF_TIME_STEPS is not found.")

