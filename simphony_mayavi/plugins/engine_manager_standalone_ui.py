from collections import namedtuple

from mayavi import mlab
from traitsui.api import View, VGroup, Group, Item

from .engine_manager import EngineManager
from .add_source_panel import AddSourcePanel
from .run_and_animate_panel import RunAndAnimatePanel


class EngineManagerStandaloneUI(EngineManager):
    ''' Standalone GUI for (1) visualising datasets from a Simphony Modeling
    Engine, (2) running the engine and (3) animating the results
    '''

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
        Panels = namedtuple("Panels",
                            ("add_source", "run_and_animate"))

        self.panels = Panels(AddSourcePanel(engine_name, engine,
                                            mayavi_engine),
                             RunAndAnimatePanel(engine, mayavi_engine))

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
        panel_views = []

        # Collect all the "panel_view" View object
        for panel in self.panels:
            view = panel.class_trait_view("panel_view")
            panel_views.append(view.content.content[0])

        all_panels = VGroup(Item("engine_name", label="Engine Wrapper"),
                            Group(*panel_views, layout="tabbed"))

        panel_mapping = {"object{}".format(index): panel
                         for index, panel in enumerate(self.panels)}
        panel_mapping["object"] = self

        for index, inner_group in enumerate(all_panels.content[1].content):
            inner_group.object = "object{}".format(index)

        self.configure_traits(view=View(all_panels, resizable=True),
                              context=panel_mapping)
