import sys
import importlib
import logging

logger = logging.getLogger(__name__)

DEFAULT_ENGINES = ("lammps_md", "kratos", "openfoam", "jyulb")


def get_factories(submodules=DEFAULT_ENGINES,
                  name="simphony_mayavi.plugins.engine_wrappers"):
    ''' Return a dictionary containing factory functions for creating
    engine wrappers.  Collect results of name.submodule.get_factories()

    If fail to load name.submodule, the submodule is passed.

    Parameters
    ----------
    submodules : sequence
        a list of submodule names (str) to be loaded
    name : str
        the module where submodules are loaded from

    Returns
    -------
    factories : dict
        {"name of the factory": callable}
    '''
    factories = dict()

    for submodule in submodules:
        # look for ``name.submodule``
        module = ".".join((name, submodule))
        try:
            importlib.import_module(module)
        except ImportError as exception:
            logger.warning(exception.message)
            logger.warning("Failed to load {}".format(module))
        else:
            factories.update(sys.modules[module].get_factories())
    return factories
