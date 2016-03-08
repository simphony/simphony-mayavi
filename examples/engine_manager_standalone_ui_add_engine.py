import simphony_mayavi.tests.testing_utils
from simphony.visualisation import mayavi_tools
from simphony_mayavi.sources.tests import testing_utils

# Dummy modeling engine for testing
engine1 = simphony_mayavi.tests.testing_utils.DummyEngine()
engine2 = simphony_mayavi.tests.testing_utils.DummyEngine()

# GUI can be initialised with an engine defined
# "test" is used as a label for representing the engine in the GUI
gui = mayavi_tools.EngineManagerStandaloneUI("test", engine1)

# add one more engine
gui.add_engine("test2", engine2)

gui.show_config()
