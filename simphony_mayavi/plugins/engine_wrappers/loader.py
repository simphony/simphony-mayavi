import sys
import importlib
import logging

logger = logging.getLogger(__name__)


def get_factories(submodules=("lammps_md", "kratos", "openfoam", "jyulb"),
                  name="simphony_mayavi.plugins.engine_wrappers"):
    ''' Return a dictionary containing factory functions for creating
    engine wrappers.  Collect results of name.submodule.get_factories()

    If fail to load name.submodule, the submodule is passed.

    Parameters
    ----------
    submodules : sequence
        a list of submodule names (str) to be loaded from
        ``name``
    name : str
        the module where submodules are loaded from

    Returns
    -------
    factories : dict
        {"name of the factory": callable}
    '''
    factories = dict()

    for submodule in submodules:
        # look for ``submodule`` in the same module as loader
        module = __name__.replace("loader", submodule)
        try:
            importlib.import_module(module)
        except ImportError as exception:
            logger.warn(exception.message)
            logger.warn("Failed to load {}".format(module))
        else:
            factories.update(sys.modules[module].get_factories())
    return factories
