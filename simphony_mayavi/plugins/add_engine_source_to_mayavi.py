from simphony_mayavi.modules.default_module import default_module
from simphony_mayavi.sources.api import EngineSource


def add_source_and_modules_to_scene(mayavi_engine, source):
    ''' Add a data source to the current Mayavi scene
    and add the modules appropriate for the data

    Parameters
    ----------
    mayavi_engine : mayavi.core.engine.Engine instance

    source : VTKDataSource
        '''
    if mayavi_engine is None:
        raise RuntimeError("mayavi_engine cannot be None")

    # add source to the current scene
    mayavi_engine.add_source(source)

    # add module to the source
    modules = default_module(source)
    for module in modules:
        mayavi_engine.add_module(module)


class AddEngineSourceToMayavi(object):

    def __init__(self, engine, mayavi_engine):
        '''
        Paramater
        ---------
        engine : Instance of ABCModelingEngine
           where dataset is extracted

        mayavi_engine : mayavi.core.engine.Engine
           for visualizing data
        '''
        self.engine = engine
        self.mayavi_engine = mayavi_engine

    def add_dataset_to_scene(self, name, **kwargs):
        ''' Add a dataset from the engine to Mayavi

        Parameters
        ----------
        name : str
            Name of the CUDS dataset to be loaded from the modeling
            engine

        \**kwargs :
            Keyword arguments accepted by CUDSSource
        '''
        source = EngineSource(engine=self.engine, dataset=name,
                              **kwargs)
        add_source_and_modules_to_scene(self.mayavi_engine, source)
