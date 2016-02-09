from mayavi import mlab


def get_mayavi2_engine_manager():
    ''' Return the EngineManager panel sitting in Mayavi2'''
    panel = mlab.get_engine().window.get_service("simphony_mayavi.plugins.engine_manager_mayavi2.EngineManagerMayavi2")  # noqa
    if panel:
        return panel
    else:
        message = ("Could not locate the EngineManager contributed by "
                   "the simphony_mayavi plugin")
        raise ValueError(message)


def add_engine_to_mayavi2(name, engine):
    ''' Add an ABCModelingEngine instance to the Mayavi2 plugin for
    SimPhoNy

    Equivalent to::

    mayavi_tools.get_mayavi2_engine_manager().add_engine(name, engine)

    Parameters
    ----------
    name : str
        Name of the Simphony Modeling Engine
    engine : ABCModelingEngine
        Simphony Modeling Engine
    '''
    get_mayavi2_engine_manager().add_engine(name, engine)
