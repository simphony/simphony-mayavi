from __future__ import print_function

import logging

from simphony.core.cuba import CUBA
from simphony.cuds.abc_modeling_engine import ABCModelingEngine
from simphony_mayavi.sources.api import EngineSource
from traits.api import HasTraits, Instance, ListStr, Button, Str, Float, Int
from traitsui.api import View, VGroup, HGroup, Item, EnumEditor

# This class is intended to be used as a standalone as well as an evisage
# plugin for mayavi.  For the latter, mayavi imports cannot be put at the
# module level or it would cause import cycles


class EngineSourceManager(HasTraits):
    ''' A basic tool for visualising CUDS datasets in a modeling
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

    One can still perform all functions of this manager withou
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

    view = View(
        VGroup(
            HGroup(Item("_dataset", label="Dataset",
                        editor=EnumEditor(name="datasets")),
                   Item("_add_to_scene", show_label=False)),

            VGroup(Item(label="Engine Settings", emphasized=True),
                   Item("_"),
                   Item("time_step"),
                   Item("number_of_time_steps"),
                   HGroup(Item(name="_number_of_runs",
                               label="Runs for"),
                          Item(label="time(s)"))),

            HGroup(Item("_animate", show_label=False))
        )
    )

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
        if self._animator:
            self._animate_delay = self._animator.delay
        if self._animator and not self._animator.ui.destroyed:
            self._animator.close()
        self._animator = self.animate(self._number_of_runs,
                                      delay=self._animate_delay)

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
    def animate(self, number_of_runs, delay=20, ui=True):
        ''' Run the modeling engine, update and thus animate the scene
        at the end of each run

        Parameters
        ----------
        number_of_runs : int
           the number of times the engine.run() is called
        delay : int
           delay between each run
        ui : bool
           whether an UI is shown
        '''
        from mayavi.mlab import animate

        @animate(delay=delay, ui=ui)
        def anim():
            for _ in xrange(number_of_runs):
                self.modeling_engine.run()
                self.update_current_sources()
                self.mayavi_engine.current_scene.render()
                yield()
        return anim()

    def update_current_sources(self):
        ''' Update all the sources in the current scene '''
        for source in self.get_current_sources():
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
        ''' Return a list of sources in the current scene

        Returns
        -------
        sources : list of EngineSource
        '''
        return self.mayavi_engine.current_scene.children

    def show_config(self):
        ''' Show the UI of this manager
        '''
        self.configure_traits(kind="live")
