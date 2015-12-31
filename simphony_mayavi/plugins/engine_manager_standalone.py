from .engine_manager import EngineManager
from .add_source_panel import AddSourcePanel
from .run_and_animate_panel import RunAndAnimatePanel


class EngineManagerStandalone(EngineManager):
    ''' Standalone Mayavi plugin for visualising CUDS from a Simphony Modeling
    Engine, running the engine and animating the results

    '''
    def __init__(self, name, modeling_engine):
        '''
        Parameters
        ----------
        name : str
            Name of the Simphony Modeling Engine wrapper
        modeling_engine : Instance of ABCModelingEngine
            Simphony Modeling Engine wrapper
        '''
        super(EngineManagerStandalone, self).__init__(name, modeling_engine)

        # Standalone Mayavi Engine
        from mayavi import mlab
        self.visual_tool = mlab.get_engine()

        # Add panels
        self.add_addon(AddSourcePanel(self.engine_name, self.current_engine,
                                      self.visual_tool))
        self.add_addon(RunAndAnimatePanel(self.engine_name, self.current_engine,
                                          self.visual_tool))
