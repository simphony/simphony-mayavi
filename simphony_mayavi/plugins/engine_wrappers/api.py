from .abc_engine_factory import ABCEngineFactory
from .kratos import ENGINE_REGISTRY as kratos_registry
from .lammps_md import ENGINE_REGISTRY as lammps_md_registry
from .jyulb import ENGINE_REGISTRY as jyulb_registry
from .openfoam import ENGINE_REGISTRY as openfoam_registry
from .loaded_engines import LOADED_ENGINES

# default engine factories
DEFAULT_ENGINE_FACTORIES = {}

# populate the default engine factories
DEFAULT_ENGINE_FACTORIES.update(kratos_registry)
DEFAULT_ENGINE_FACTORIES.update(lammps_md_registry)
DEFAULT_ENGINE_FACTORIES.update(jyulb_registry)
DEFAULT_ENGINE_FACTORIES.update(openfoam_registry)

# Filter the ones not imported
DEFAULT_ENGINE_FACTORIES = {
    name: factory
    for name, factory in DEFAULT_ENGINE_FACTORIES.items()
    if name in LOADED_ENGINES
}


__all__ = ["ABCEngineFactory", "DEFAULT_ENGINE_FACTORIES"]
