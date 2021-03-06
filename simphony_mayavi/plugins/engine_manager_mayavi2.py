import logging

from traits.api import Instance, List, on_trait_change
from traitsui.api import View, VGroup, Group, Item
from envisage.api import Plugin, ServiceOffer

# EngineManager imports mayavi.core.trait_defs in the module level
from simphony_mayavi.plugins.engine_manager import EngineManager
from simphony_mayavi.plugins.tabbed_panel_collection import (
    TabbedPanelCollection)

# More internal mayavi imports are done within EngineManagerMayavi2 to
# avoid import cycles when the class is imported as a Mayavi2 plugin

logger = logging.getLogger(__name__)


class EngineManagerMayavi2(EngineManager):
    """ The Simphony panel in the Mayavi2 application """

    #: The workbench window
    window = Instance("pyface.workbench.api.WorkbenchWindow")

    #: The panels
    panels = Instance(TabbedPanelCollection)

    view = View(
        VGroup(
            Group(Item("engine_name", label="Engine Wrapper")),
            Group(Item("panels", style="custom", show_label=False))),
        resizable=True)

    def get_mayavi(self):
        '''Get the mayavi engine in Mayavi2'''
        from mayavi.core.engine import Engine
        return self.window.get_service(Engine)

    def _window_changed(self):
        self._set_panels()

    def _set_panels(self):
        # mayavi imports here to avoid import cycle
        from simphony_mayavi.plugins.add_source_panel import AddSourcePanel
        from simphony_mayavi.plugins.run_and_animate_panel import (
            RunAndAnimatePanel)
        from simphony_mayavi.plugins.add_engine_panel import AddEnginePanel

        # Mayavi engine from the Mayavi2
        mayavi_engine = self.get_mayavi()

        # Add panels
        self.panels = TabbedPanelCollection.create(
            add_engine=AddEnginePanel(engine_manager=self),
            add_source=AddSourcePanel(engine_name=self.engine_name,
                                      engine=self.engine,
                                      mayavi_engine=mayavi_engine),
            run_and_animate=RunAndAnimatePanel(engine=self.engine,
                                               mayavi_engine=mayavi_engine))

        logger.info("Simphony EngineManagerMayavi2 panel setup completed")

    def _engine_name_changed(self):
        for panel in self.panels:
            panel.engine = self.engine
        self.panels.add_source.engine_name = self.engine_name


class EngineManagerMayavi2Plugin(Plugin):

    SERVICE_OFFERS = "envisage.ui.workbench.service_offers"
    VIEWS = "envisage.ui.workbench.views"

    service_offers = List(contributes_to=SERVICE_OFFERS)
    views = List(contributes_to=VIEWS)

    # Private methods.
    def _service_offers_default(self):
        """ Trait initializer. """
        worker_service_offer = ServiceOffer(
            protocol='simphony_mayavi.plugins.engine_manager_mayavi2.EngineManagerMayavi2',  # noqa
            factory='simphony_mayavi.plugins.engine_manager_mayavi2.EngineManagerMayavi2'  # noqa
        )
        return [worker_service_offer]

    def _views_default(self):
        """ Trait initializer. """
        return [self._worker_view_factory]

    def _worker_view_factory(self, window, **traits):
        """ Factory method for the current selection of the engine. """

        from pyface.workbench.traits_ui_view import TraitsUIView

        worker = window.get_service(('simphony_mayavi.plugins.'
                                     'engine_manager_mayavi2.'
                                     'EngineManagerMayavi2'))
        tui_worker_view = TraitsUIView(
            obj=worker,
            view='view',
            id='user_mayavi.EngineManagerMayavi2.view',
            name='Simphony',
            window=window,
            position='left',
            **traits
        )
        return tui_worker_view

    @on_trait_change("application.gui:started")
    def _on_application_gui_started(self, obj, trait_name, old, new):

        if trait_name != "started" or not new:
            return

        # Bind the EngineManagerMayavi2 instance to ``simphony_panel``

        SHELL_VIEW = "envisage.plugins.python_shell_view"
        window = self.application.workbench.active_window

        # python shell
        py = window.get_view_by_id(SHELL_VIEW)

        # EngineManagerMayavi2 instance
        worker = window.get_service(('simphony_mayavi.plugins.'
                                     'engine_manager_mayavi2.'
                                     'EngineManagerMayavi2'))
        if py is None:
            logger.warn("*"*80)
            logger.warn("Cannot find the Python shell")
        else:
            try:
                py.bind("simphony_panel", worker)
            except AttributeError as exception:
                logger.warn(exception.message)
                logger.warn("Cannot bind simphony_panel to the Python shell")
            else:
                logger.info("binded ``simphony_panel`` to the Python shell")
