from .abc_engine_factory import ABCEngineFactory


class JyulbFileIOEngineFactory(ABCEngineFactory):

    def create(self):
        from simphony.engine import jyulb_fileio_isothermal
        return jyulb_fileio_isothermal.JYULBEngine()


class JyulbInternalEngineFactory(ABCEngineFactory):

    def create(self):
        from simphony.engine import jyulb_internal_isothermal
        return jyulb_internal_isothermal.JYULBEngine()


ENGINE_REGISTRY = dict(jyulb_fileio_isothermal=JyulbFileIOEngineFactory(),
                       jyulb_internal_isothermal=JyulbInternalEngineFactory())
