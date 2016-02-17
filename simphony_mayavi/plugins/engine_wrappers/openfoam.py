from .abc_engine_factory import ABCEngineFactory


class OpenFoamFileIOEngineFactory(ABCEngineFactory):

    def create(self):
        from simphony.engine import openfoam_file_io
        return openfoam_file_io.FoamControlWrapper()


class OpenFoamInternalEngineFactory(ABCEngineFactory):

    def create(self):
        from simphony.engine import openfoam_internal
        return openfoam_internal.FoamInternalWrapper()


ENGINE_REGISTRY = dict(openfoam_file_io=OpenFoamFileIOEngineFactory(),
                       openfoam_internal=OpenFoamInternalEngineFactory())
