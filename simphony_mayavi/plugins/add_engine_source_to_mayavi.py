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

    def add_dataset_to_scene(self, name,
                             point_scalars_name=None, point_vectors_name=None,
                             cell_scalars_name=None, cell_vectors_name=None):
        ''' Add a dataset from the engine to Mayavi

        Parameters
        ----------
        name : str
            name of the CUDS dataset to be added
            Check self.engine.get_dataset_names() to see available
            dataset names.
        point_scalars_name : str, optional
            CUBA name of the data to be selected as point scalars.
            default is the first available point scalars data
        point_vectors_name : str, optional
            CUBA name of the data to be selected as point vectors
            default is the first available point vectors data
        cell_scalars_name : str, optional
            CUBA name of the data to be selected as cell scalars
            default is the first available cell scalars data
        cell_vectors_name : str, optional
            CUBA name of the data to be selected as cell vectors
            default is the first available cell vectors data

        To turn off visualisation of a point/cell data, assign
        [point/cell]_[scalars/vectors]_name to an empty string (i.e. "")
        '''
        source = EngineSource(self.engine)
        source.dataset = name
        if point_scalars_name is not None:
            source.point_scalars_name = point_scalars_name
        if point_vectors_name is not None:
            source.point_vectors_name = point_vectors_name
        if cell_scalars_name is not None:
            source.cell_scalars_name = cell_scalars_name
        if cell_vectors_name is not None:
            source.cell_vectors_name = cell_vectors_name
        add_source_and_modules_to_scene(self.mayavi_engine, source)
