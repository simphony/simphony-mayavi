import logging

from traits.api import Float, Int, Button, Bool, HasTraits
from traitsui.api import View, VGroup, HGroup, Item, message

from simphony.core.cuba import CUBA

from .basic_panel import BasicPanel


class RunAndAnimatePanel(BasicPanel):
    '''
    Attributes
    ----------
    time_step : float
        CUBA.TIME_STEP of the Simphony Engine
    number_of_time_steps : float
        CUBA.NUMBER_OF_TIME_STEPS of the Simphony Engine
    '''

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

    panel_view = View(VGroup(
        Item("time_step"),
        Item("number_of_time_steps"),
        HGroup(Item(name="_number_of_runs", label="Runs for"),
               Item(label="time(s)")),
        HGroup(Item("_animate", show_label=False),
               Item(name="_update_all_scenes", label="Update all scenes")),
        label="Run/Animate"))

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

    def _engine_name_changed(self):
        self._setup_run_parameters()

    # ---------------------------------------------------------
    # References to all the public methods
    # ---------------------------------------------------------
    def _get_public_methods(self):
        return (self.animate,)

    # ----------------------------------------------------------
    # Public methods
    # ----------------------------------------------------------

    def animate(self, number_of_runs, delay=None, ui=True,
                update_all_scenes=False):
        ''' Run the modeling engine, and animate the scene

        If there is no source in the scene or none of the sources is
        an EngineSource representing a dataset from ``engine``,
        a RuntimeError is raised.

        Parameters
        ----------
        number_of_runs : int
           the number of times the engine.run() is called
        delay : int (optional)
           delay between each run.
           If None, use previous setting or Mayavi's default: 500
        ui : bool
           whether an UI is shown
        update_all_scenes : bool
           whether all scenes are updated

        Raises
        ------
        RuntimeError
            if no EngineSource belongs to ``engine`` is found
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
            get_sources_func = self._get_all_sources
        else:
            get_sources_func = self._get_current_sources

        try:
            sources = get_sources_func()
        except AttributeError:
            text = "Nothing in scene. Engine is not run"
            message(text)
            raise RuntimeError(text)

        if len(sources) == 0:
            text = ("Nothing in scene belongs to the Engine.\n"
                    "Engine is not run.")
            message(text)
            raise RuntimeError(text)

        @animate(delay=delay, ui=ui)
        def anim():
            for _ in xrange(number_of_runs):
                self.engine.run()
                self._update_sources(sources)
                self.visual_tool.current_scene.render()
                yield()
        self._animator = anim()

    # ---------------------------------------------------------
    # Private methods
    # ---------------------------------------------------------

    def _update_sources(self, sources):
        ''' Update multiple sources in scene'''
        for source in sources:
            source.update()

    def _get_current_sources(self):
        ''' Return the current scene's sources that belong
        to this manager's modeling engine
        Note that this is not a Trait Property getter

        Returns
        -------
        sources : set of EngineSource
        '''
        sources = self.visual_tool.current_scene.children
        return {source for source in sources
                if source.engine == self.engine}

    def _get_all_sources(self):
        ''' Return sources from all the scenes and that the sources
        belong to this manager's modeling engine

        Returns
        -------
        sources : set of EngineSource
        '''
        sources = {source
                   for scene in self.visual_tool.scenes
                   for source in scene.children
                   if source.engine == self.engine}
        return sources

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
