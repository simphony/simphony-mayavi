from simphony.visualisation import mayavi_tools
from simphony_mayavi.sources.tests.testing_utils import DummyEngine


# Dummy Modeling Engine for demostration
# The dummy engine has datasets "particles", "lattice", "mesh"
modeling_engine = DummyEngine()

manager = mayavi_tools.EngineManagerStandalone(modeling_engine)

# visualise "particles"
manager.add_dataset_to_scene("particles")

# run the engine for 100 times and animate the
# visualised "particles" after each run
# show a GUI for control the speed of animation
manager.animate(100, delay=100, ui=True)
