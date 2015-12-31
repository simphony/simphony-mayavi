from traits.api import Instance

from .engine_manager import EngineManager


# mayavi cannot be imported at the module level to avoid
# import cycles when EngineManagerMayavi2 is imported as
# Mayavi2 plugin


class EngineManagerMayavi2(EngineManager):
    window = Instance("pyface.workbench.api.WorkbenchWindow")

    def __init__(self, name, modeling_engine):
        self.add_engine(name, modeling_engine)

        from mayavi.plugins.script import Script
        self.visual_tool = self.window.get_service(Script)
