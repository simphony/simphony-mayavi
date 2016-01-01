from traits.api import HasTraits, Instance, Str, Any, Property

from simphony.cuds.abc_modeling_engine import ABCModelingEngine


class BasicPanel(HasTraits):
    '''
    Attributes
    ----------
    engine : Instance of ABCModelingEngine
        Simphony Modeling Engine wrapper
    engine_name : str
        Name of the modeling engine
    visual_tool : Any
        for visualization
    '''
    engine = Instance(ABCModelingEngine)
    engine_name = Str
    visual_tool = Any
