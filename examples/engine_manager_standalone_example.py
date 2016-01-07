from simphony.visualisation import mayavi_tools
from simphony_mayavi.sources.tests import testing_utils


# Dummy Modeling Engine
# The dummy engine has datasets "particles", "lattice", "mesh"
modeling_engine = testing_utils.DummyEngine()

manager = mayavi_tools.EngineManagerStandalone(modeling_engine)

# visualise "particles"
manager.add_dataset_to_scene("particles")

# run the engine for 100 times and animate the
# visualised "particles" after each run
# show a GUI for control the speed of animation
manager.animate(100, delay=100, ui=True)
