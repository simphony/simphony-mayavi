from traits.api import HasTraits, Instance, Str, Any, Property

from simphony.cuds.abc_modeling_engine import ABCModelingEngine


class BasicPanel(HasTraits):
    engine = Instance(ABCModelingEngine)
    engine_name = Str
    visual_tool = Any
    public_methods = Property

    def __init__(self, engine_name, engine, visual_tool):
        ''' Initialization

        Parameters
        ----------
        engine_name : str
        engine : Instance of ABCModelingEngine
            Simphony Engine Wrapper
        visual_tool : Any
            For visualisation
        '''
        self.engine_name = engine_name
        self.engine = engine
        self.visual_tool = visual_tool
