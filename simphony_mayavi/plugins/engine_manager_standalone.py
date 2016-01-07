from collections import namedtuple
from functools import wraps

from mayavi import mlab

from .add_engine_source_to_mayavi import AddEngineSourceToMayavi
from .run_and_animate import RunAndAnimate


class EngineManagerStandalone(object):
    ''' Standalone non-GUI manager for (1) visualising datasets from
    a Simphony Modeling Engine, (2) running the engine and (3) animating
    the results

    Parameters
    ----------
    engine : Instance of ABCModelingEngine
    mayavi_engine : mayavi.core.engine.Engine
        default to be mayavi.mlab.get_engine()
   '''
    def __init__(self, engine, mayavi_engine=None):
        '''
        Parameters
        ----------
        engine : Instance of ABCModelingEngine
        mayavi_engine : mayavi.core.engine.Engine (option)
            default to be mayavi.mlab.get_engine()
        '''
        self.engine = engine

        if mayavi_engine is None:
            self.mayavi_engine = mlab.get_engine()
        else:
            self.mayavi_engine = mayavi_engine

        Addons = namedtuple("Addons",
                            ("add_source", "run_and_animate"))

        self.addons = Addons(AddEngineSourceToMayavi(self.engine,
                                                     self.mayavi_engine),
                             RunAndAnimate(self.engine, self.mayavi_engine))

    @wraps(AddEngineSourceToMayavi.add_dataset_to_scene)
    def add_dataset_to_scene(self, *args, **kwargs):
        self.addons.add_source.engine = self.engine
        self.addons.add_source.add_dataset_to_scene(*args, **kwargs)

    @wraps(RunAndAnimate.animate)
    def animate(self, *args, **kwargs):
        self.addons.run_and_animate.engine = self.engine
        self.addons.run_and_animate.animate(*args, **kwargs)
