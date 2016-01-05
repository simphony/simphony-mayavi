from collections import namedtuple

from traits.api import Instance
from traitsui.api import View, VGroup, Group, Item

from .engine_manager_standalone_ui import EngineManagerStandaloneUI
from .add_source_panel import AddSourcePanel
from .run_and_animate_panel import RunAndAnimatePanel


# mayavi cannot be imported at the module level to avoid
# import cycles when EngineManagerMayavi2 is imported as
# Mayavi2 plugin


class EngineManagerMayavi2(EngineManagerStandaloneUI):

    window = Instance("pyface.workbench.api.WorkbenchWindow")

    def __init__(self):
        from mayavi.plugins.script import Script
        self.mayavi_engine = self.window.get_service(Script)
        
        # Add panels
        Panels = namedtuple("Panels",
                            ("add_source", "run_and_animate"))

        self.panels = Panels(AddSourcePanel(self.engine_name, self.engine,
                                            self.mayavi_engine),
                             RunAndAnimatePanel(self.engine, self.mayavi_engine))
