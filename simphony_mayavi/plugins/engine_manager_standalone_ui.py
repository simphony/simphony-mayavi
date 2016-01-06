from mayavi import mlab
from traitsui.api import View, VGroup, Group, Item
from traits.api import Instance

from simphony_mayavi.plugins.engine_manager import EngineManager
from simphony_mayavi.plugins.add_source_panel import AddSourcePanel
from simphony_mayavi.plugins.run_and_animate_panel import RunAndAnimatePanel
from simphony_mayavi.plugins.trait_namedtuple import TraitNamedTuple


class EngineManagerStandaloneUI(EngineManager):
    ''' Standalone GUI for (1) visualising datasets from a Simphony Modeling
    Engine, (2) running the engine and (3) animating the results
    '''

    panels = Instance(TraitNamedTuple)

    traits_view = View(
        VGroup(
            Group(Item("engine_name", label="Engine Wrapper")),
            Group(Item("panels", style="custom", show_label=False)))
    )

    def __init__(self, engine_name, engine, mayavi_engine=None):
        '''
        Parameters
        ----------
        engine_name : str
            Name of the Simphony Modeling Engine wrapper
        engine : Instance of ABCModelingEngine
            Simphony Modeling Engine wrapper
        mayavi_engine : mayavi.core.engine.Engine
            Default to be mayavi.mlab.get_engine()
        '''
        if mayavi_engine is None:
            # Standalone Mayavi Engine
            mayavi_engine = mlab.get_engine()
        else:
            mayavi_engine = mayavi_engine

        # Add panels
        self.panels = TraitNamedTuple(
            add_source=AddSourcePanel(engine_name, engine, mayavi_engine),
            run_and_animate=RunAndAnimatePanel(engine, mayavi_engine))
        self.add_engine(engine_name, engine)

    def _engine_name_changed(self):
        # Sync panels when engine_name (i.e. engine) changes
        for panel in self.panels:
            panel.engine = self.engine
        self.panels.add_source.engine_name = self.engine_name

    # --------------------------------------------------------------
    # Public methods
    # --------------------------------------------------------------

    def show_config(self):
        ''' Show the GUI with all the panels '''
        self.configure_traits()
