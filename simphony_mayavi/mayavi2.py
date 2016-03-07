""" This module provides end-user functions for interacting with
the SimPhoNy panel in Mayavi2 application
"""
from mayavi.core.registry import registry
from mayavi.plugins.envisage_engine import EnvisageEngine


def get_simphony_panel():
    ''' Return the SimPhoNy panel object sitting in Mayavi2

    Returns
    -------
    panel : EngineManagerMayavi2

    Raises
    ------
    RuntimeError
        If the Mayavi2 application is not found or
        the SimPhoNy panel is not found in the application
    '''
    # Look for EnvisageEngine
    # We don't use `mlab.get_engine` here because the behaviour of
    # `mlab.get_engine` depends on `mlab.options.backend`,
    # `mlab.options.offscreen` and whether user has manually registered
    # mayavi engines.  Here we just want to look for a registered
    # EnvisageEngine and raise an Error if it is not found
    for engine in registry.engines.values():
        if isinstance(engine, EnvisageEngine):
            break
    else:
        message = "No registered EnvisageEngine. Is Mayavi2 running?"
        raise RuntimeError(message)

    # The Simphony Panel (plugin) should be a registered service
    panel = engine.window.get_service(
        "simphony_mayavi.plugins.engine_manager_mayavi2.EngineManagerMayavi2")

    if panel:
        return panel
    else:
        # It is possible if the user has not activated the
        # simphony_mayavi plugin in Mayavi2
        message = ("Could not locate the SimPhoNy panel contributed by "
                   "the simphony_mayavi plugin")
        raise RuntimeError(message)


def add_engine_to_mayavi2(name, engine):
    ''' Add an ABCModelingEngine instance to the Mayavi2 plugin for
    SimPhoNy

    Parameters
    ----------
    name : str
        Name of the Simphony Modeling Engine

    engine : ABCModelingEngine
        Simphony Modeling Engine
    '''
    get_simphony_panel().add_engine(name, engine)
