from .abc_engine_factory import ABCEngineFactory
from .kratos import ENGINE_REGISTRY as kratos_registry
from .lammps_md import ENGINE_REGISTRY as lammps_md_registry
from .jyulb import ENGINE_REGISTRY as jyulb_registry
from .openfoam import ENGINE_REGISTRY as openfoam_registry

# default engine factories
DEFAULT_ENGINE_FACTORIES = {}

# populate the default engine factories
DEFAULT_ENGINE_FACTORIES.update(kratos_registry)
DEFAULT_ENGINE_FACTORIES.update(lammps_md_registry)
DEFAULT_ENGINE_FACTORIES.update(jyulb_registry)
DEFAULT_ENGINE_FACTORIES.update(openfoam_registry)


def get_loaded_engine_extensions():
    ''' Return the extension names in simphony.engine '''
    from stevedore import extension
    mgr = extension.ExtensionManager(
        namespace="simphony.engine",
        invoke_on_load=False)
    return tuple(extension.name for extension in mgr.extensions)


LOADED_ENGINE_EXTENSIONS = get_loaded_engine_extensions()


# Filter the ones not imported
DEFAULT_ENGINE_FACTORIES = {
    name: factory
    for name, factory in DEFAULT_ENGINE_FACTORIES.items()
    if name in LOADED_ENGINE_EXTENSIONS
}


__all__ = ["ABCEngineFactory", "DEFAULT_ENGINE_FACTORIES"]
