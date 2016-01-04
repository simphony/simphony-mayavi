import logging

from mayavi.mlab import animate


class RunAndAnimate(object):

    def __init__(self, engine, mayavi_engine):
        '''
        Parameters
        ----------
        engine : Instance of ABCModelingEngine
        mayavi_engine : Instance of mayavi.core.engine.Engine
        '''
        self.engine = engine
        self.mayavi_engine = mayavi_engine

        self._animator = None
        self._isrunning = False

    @property
    def isrunning(self):
        ''' Status of the animator '''
        return (self._isrunning and
                self._animator and self._animator.timer.IsRunning())

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
        delay : int, optional
           delay between each run.
           If None, use previous setting or Mayavi's default: 500
        ui : bool, optional
           whether an UI is shown, default is True
        update_all_scenes : bool, optional
           whether all scenes are updated, default is False

        Raises
        ------
        RuntimeError
            if no EngineSource belongs to ``engine`` is found
        '''
        # remember the last delay being set
        if delay is None:
            if self._animator:
                delay = self._animator.delay
            else:
                delay = 500

        # close the old window and start a new one
        # FIXME: there should be a better way
        if (self._animator and self._animator.ui and
                not self._animator.ui.destroyed):
            self._animator.close()

        if update_all_scenes:
            get_sources_func = self._get_all_sources
        else:
            get_sources_func = self._get_current_sources

        try:
            sources = get_sources_func()
        except AttributeError:
            message = "Nothing in scene. Engine is not run"
            raise RuntimeError(message)

        if len(sources) == 0:
            message = ("Nothing in scene belongs to the Engine.\n"
                       "Engine is not run.")
            raise RuntimeError(message)

        @animate(delay=delay, ui=ui)
        def anim():
            self._isrunning = True

            # keep a reference to the engine being run
            engine_on_start = self.engine

            for _ in xrange(number_of_runs):
                if self.engine is not engine_on_start:
                    message = "Engine changed while animating. Stop running"
                    logging.warning(message)
                    break
                self.engine.run()
                self._update_sources(sources)
                self.mayavi_engine.current_scene.render()
                yield
            self._isrunning = False

        self._animator = anim()

    # -------------------------------------------------
    # Private methods
    # -------------------------------------------------

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
        sources = self.mayavi_engine.current_scene.children
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
                   for scene in self.mayavi_engine.scenes
                   for source in scene.children
                   if source.engine == self.engine}
        return sources
