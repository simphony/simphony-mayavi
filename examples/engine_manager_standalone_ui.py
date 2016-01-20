from simphony_mayavi.sources.tests.testing_utils import DummyEngine
from simphony.visualisation import mayavi_tools

# GUI for Interacting with the engine and mayavi
gui = mayavi_tools.EngineManagerStandaloneUI()

gui.show_config()

# you can add an engine from the python shell
engine_wrapper = DummyEngine()

# "test" is used as a label for representing the engine in the GUI
gui.add_engine("test", engine_wrapper)

# you can remove the engine from the GUI
# Notice that this may not destroy the instance if the instance
# is referenced elsewhere (i.e. ``engine_wrapper``)
gui.remove_engine("test")
