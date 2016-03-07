from mayavi.tools.engine_manager import get_engine as get_mayavi_engine
from mayavi.tools.engine_manager import options as mayavi_options


def get_simphony_panel():
    ''' Return the SimPhoNy panel object sitting in Mayavi2

    Returns
    -------
    panel : :class:`simphony_mayavi.plugins.engine_manager.EngineManager`

    Raises
    ------
    AttributeError
        If the Mayavi2 application window is not found or
        the SimPhoNy panel is not found
    '''
    # Ensure the Mayavi Engine is an EnvisageEngine
    old_backend = mayavi_options.backend
    mayavi_options.backend = "envisage"

    # Look for the application window from the EnvisageEngine
    try:
        window = get_mayavi_engine().window
    except AttributeError:
        message = "Failed to find the application window. Is Mayavi2 running?"
        raise AttributeError(message)
    finally:
        # Whatever happens, reset the backend
        mayavi_options.backend = old_backend

    # The Simphony Panel (plugin) should be a registered service
    panel = window.get_service("simphony_mayavi.plugins.engine_manager_mayavi2.EngineManagerMayavi2")  # noqa

    if panel:
        return panel
    else:
        # It is possible if the user has not activated the
        # simphony_mayavi plugin in Mayavi2
        message = ("Could not locate the SimPhoNy panel contributed by "
                   "the simphony_mayavi plugin")
        raise AttributeError(message)


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
