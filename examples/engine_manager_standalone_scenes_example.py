from simphony_mayavi.tests.testing_utils import DummyEngine
from simphony.visualisation import mayavi_tools


# Dummy Modeling Engine
# The dummy engine has datasets "particles", "lattice", "mesh"
modeling_engine = DummyEngine()

manager = mayavi_tools.EngineManagerStandalone(modeling_engine)

# visualise "particles" to scene 1
manager.add_dataset_to_scene("particles")

# add a new scene
manager.mayavi_engine.new_scene()

# visualise "lattice" in the new scene
# choose to visualise "temperature" as the point scalar data
manager.add_dataset_to_scene("lattice", "TEMPERATURE")

# run the engine for 100 times and animate the
# datasets in all scenes
manager.animate(100, delay=100, ui=True, update_all_scenes=True)
