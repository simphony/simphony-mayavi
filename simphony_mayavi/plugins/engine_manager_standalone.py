from traitsui.api import View, VGroup, Group, Item

from .engine_manager import EngineManager
from .add_source_panel import AddSourcePanel
from .run_and_animate_panel import RunAndAnimatePanel
from .basic_panel import BasicPanel

class EngineManagerStandalone(EngineManager, AddSourcePanel, RunAndAnimatePanel):
    ''' Standalone Mayavi plugin for visualising CUDS from a Simphony Modeling
    Engine, running the engine and animating the results

    Attributes
    ----------
    engine : Instance of ABCModelingEngine
        Currently selected Simphony Modeling Engine wrapper
    engine_name : str
        Name of engine
    visual_tool : mayavi.core.engine.Engine
        Default to be mayavi.mlab.get_engine()
    engines : dict
        All Simphony Modeling Engine wrappers in the manager
    time_step : float
        CUBA.TIME_STEP of the Simphony Engine
    number_of_time_steps : float
        CUBA.NUMBER_OF_TIME_STEPS of the Simphony Engine
    '''
    def __init__(self, engine_name, engine, visual_tool=None):
        '''
        Parameters
        ----------
        engine_name : str
            Name of the Simphony Modeling Engine wrapper
        engine : Instance of ABCModelingEngine
            Simphony Modeling Engine wrapper
        visual_tool : mayavi.core.engine.Engine
            Default to be mayavi.mlab.get_engine()
        
        '''
        # EngineManager.add_engine
        self.add_engine(engine_name, engine)

        if visual_tool is None:
            # Standalone Mayavi Engine
            from mayavi import mlab
            self.visual_tool = mlab.get_engine()

    def show_config(self):
        ''' Show the GUI with all the panels '''
        panel_views = []

        # Collect all the "panel_view" View object
        for cls in self.__class__.__mro__[2:]:
            if not issubclass(cls, BasicPanel):
                continue

            view = cls.class_trait_view("panel_view")

            if view is not None:
                panel_views.append(view.content.content[0])

        all_panels = VGroup(Item("engine_name", label="Engine Wrapper"),
                            Group(*panel_views, layout="tabbed"))
        self.edit_traits(view=View(all_panels))

