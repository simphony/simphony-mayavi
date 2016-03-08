from simphony_mayavi.tests.testing_utils import DummyEngine
from simphony.visualisation import mayavi_tools

# Dummy modeling engine for testing
engine1 = DummyEngine()
engine2 = DummyEngine()

# GUI can be initialised with an engine defined
# "test" is used as a label for representing the engine in the GUI
gui = mayavi_tools.EngineManagerStandaloneUI("test", engine1)

# add one more engine
gui.add_engine("test2", engine2)

gui.show_config()
