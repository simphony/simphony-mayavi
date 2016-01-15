from simphony.visualisation import mayavi_tools
from simphony_mayavi.sources.tests import testing_utils

# Dummy modeling engine for testing
engine = testing_utils.DummyEngine()

# GUI for Interacting with the engine and mayavi
# "test" is used as a label for representing the engine in the GUI
gui = mayavi_tools.EngineManagerStandaloneUI("test", engine)

gui.show_config()
