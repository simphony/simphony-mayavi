from mayavi import mlab
from traitsui.api import View, VGroup, Group, Item
from traits.api import HasTraits, Instance

from simphony_mayavi.plugins.engine_manager import EngineManager
from simphony_mayavi.plugins.add_engine_panel import AddEnginePanel
from simphony_mayavi.plugins.add_source_panel import AddSourcePanel
from simphony_mayavi.plugins.run_and_animate_panel import RunAndAnimatePanel
from simphony_mayavi.plugins.tabbed_panel_collection import (
    TabbedPanelCollection)


class EngineManagerStandaloneUI(EngineManager):
    ''' Standalone GUI for visualising datasets from a Simphony Modeling
    Engine, running the engine and animating the results

    '''

    panels = Instance(TabbedPanelCollection)

    traits_view = View(
        VGroup(
            Group(Item("engine_name", label="Engine Wrapper")),
            Group(Item("panels", style="custom", show_label=False))),
        title="Engine Manager",
        resizable=True)

    def __init__(self, engine_name="", engine=None, mayavi_engine=None):
        '''
        Parameters
        ----------
        engine_name : str
            Name of the Simphony Modeling Engine wrapper

        engine : ABCModelingEngine
            Simphony Modeling Engine wrapper

        mayavi_engine : mayavi.core.engine
            Default to be mayavi.mlab.get_engine()

        '''
        # Traits initialisation
        HasTraits.__init__(self)

        if mayavi_engine is None:
            # Standalone Mayavi Engine
            mayavi_engine = mlab.get_engine()
        else:
            mayavi_engine = mayavi_engine

        # Add panels
        self.panels = TabbedPanelCollection.create(
            add_engine=AddEnginePanel(engine_manager=self),
            add_source=AddSourcePanel(engine_name=self.engine_name,
                                      engine=self.engine,
                                      mayavi_engine=mayavi_engine),
            run_and_animate=RunAndAnimatePanel(engine=self.engine,
                                               mayavi_engine=mayavi_engine))

        if engine and engine_name:
            self.add_engine(engine_name, engine)

    def _engine_name_changed(self):
        # Sync panels when engine_name (i.e. engine) changes
        for panel in self.panels:
            if hasattr(panel, "engine"):
                panel.engine = self.engine
        self.panels.add_source.engine_name = self.engine_name

    # --------------------------------------------------------------
    # Public methods
    # --------------------------------------------------------------

    def show_config(self):
        ''' Show the GUI with all the panels '''
        return self.edit_traits()
