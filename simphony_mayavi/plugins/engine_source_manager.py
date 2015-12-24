from __future__ import print_function

import logging

from simphony.core.cuba import CUBA
from simphony.cuds.abc_modeling_engine import ABCModelingEngine
from simphony_mayavi.sources.api import EngineSource
from traits.api import (HasTraits, Instance, ListStr, Button, Str, Float, Int,
                        Bool)
from traitsui.api import View, VGroup, HGroup, Item, EnumEditor, message

# This class is intended to be used as a standalone as well as an evisage
# plugin for mayavi.  For the latter, mayavi imports cannot be put at the
# module level or it would cause import cycles


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
    >>> manager = EngineSourceManager(dem)
    >>> manager.show_config()   # GUI

    One can still perform all functions of this manager without
    opening up a GUI ::

    >>> from simphony_mayavi.plugins.api import EngineSourceManager
    >>> manager = EngineSourceManager(dem)
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

    # ----------------------------------------------
    # Basic Info of the modeling engine
    # ----------------------------------------------
    modeling_engine = Instance(ABCModelingEngine, allow_none=False)
    datasets = ListStr
    _dataset = Str

    # -------------------------------------------------------
    # Basic time step parameters to interact with the engine
    # -------------------------------------------------------
    time_step = Float(allow_none=False)
    number_of_time_steps = Float(allow_none=False)

    # ----------------------------------------------
    # only relevant to UI
    # ----------------------------------------------
    _number_of_runs = Int(1)
    _add_to_scene = Button("Add to scene")
    _animate = Button("Animate")
    _animator = None
    _animate_delay = 20
    _update_all_scenes = Bool(False)

    view = View(
        VGroup(
            HGroup(Item("_dataset", label="Dataset",
                        editor=EnumEditor(name="datasets")),
                   Item("_add_to_scene", show_label=False)),

            Item(label="Engine Settings", emphasized=True),
            Item("_"),
            Item("time_step"),
            Item("number_of_time_steps"),
            HGroup(Item(name="_number_of_runs",
                        label="Runs for"),
                   Item(label="time(s)")),

            HGroup(Item("_animate", show_label=False),
                   Item(name="_update_all_scenes",
                        label="Update all scenes"))))

    # ------------------------------------------------
    # Public property
    # ------------------------------------------------
    @property
    def datasets(self):
        """ Datasets (list) in the modeling engines """
        return self.modeling_engine.get_dataset_names()

    # ----------------------------------------------------
    # Initialization
    # ----------------------------------------------------
    def __init__(self, modeling_engine, as_plugin=False):
        # SimPhoNy Modeling Engine wrapper
        self.modeling_engine = modeling_engine

        # default dataset
        if self.datasets:
            self._dataset = self.datasets[0]

        # For interacting with the engine
        if CUBA.TIME_STEP in self.modeling_engine.CM:
            self.time_step = self.modeling_engine.CM[CUBA.TIME_STEP]
        else:
            logging.warning("TIME_STEP is not found.")

        if CUBA.NUMBER_OF_TIME_STEPS in self.modeling_engine.CM:
            value = self.modeling_engine.CM[CUBA.NUMBER_OF_TIME_STEPS]
            self.number_of_time_steps = value
        else:
            logging.warning("NUMBER_OF_TIME_STEPS is not found.")

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
    def __add_to_scene_fired(self):
        self.add_dataset_to_scene(self._dataset)

    def __animate_fired(self):
        self.animate(self._number_of_runs,
                     update_all_scenes=self._update_all_scenes)

    # ----------------------------------------------------------
    # Trait handlers
    # ----------------------------------------------------------
    def _time_step_changed(self):
        self.modeling_engine.CM[CUBA.TIME_STEP] = self.time_step

    def _number_of_time_steps_changed(self):
        value = self.number_of_time_steps
        self.modeling_engine.CM[CUBA.NUMBER_OF_TIME_STEPS] = value

    # -----------------------------------------------------------
    # Public methods
    # -----------------------------------------------------------
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
                self.modeling_engine.run()
                self.update_sources(sources)
                self.mayavi_engine.current_scene.render()
                yield()
        self._animator = anim()

    def update_sources(self, sources):
        ''' Update multiple sources'''
        for source in sources:
            source.update()

    def add_dataset_to_scene(self, name, module=None):
        from simphony_mayavi.modules.default_module import default_module

        source = EngineSource(engine=self.modeling_engine)
        source.dataset = name
        self.mayavi_engine.add_source(source)

        # add module to the source
        if module:
            self.mayavi_engine.add_module(module)
        else:
            self.mayavi_engine.add_module(default_module(source._vtk_cuds))

    def get_current_sources(self):
        ''' Return the current scene's sources that are belong
        to this manager's modeling engine

        Returns
        -------
        sources : set of EngineSource
        '''
        sources = self.mayavi_engine.current_scene.children
        return {source for source in sources
                if source.engine == self.modeling_engine}

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
                   if source.engine == self.modeling_engine}
        return sources

    def show_config(self):
        ''' Show the UI of this manager
        '''
        self.configure_traits(kind="live")
