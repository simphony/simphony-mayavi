from mayavi import mlab

from simphony_mayavi.sources.tests.testing_utils import DummyEngine
from simphony_mayavi.sources.api import EngineSource


# Comply to SimPhoNy modeling engine API
engine_wrapper = DummyEngine()

# Define EngineSource, choose dataset
src = EngineSource(engine=engine_wrapper,
                   dataset="particles")

# choose the CUBA attribute for display
src.point_scalars_name = "TEMPERATURE"

# use glyph to show the particles
mlab.pipeline.glyph(src, scale_factor=0.2, scale_mode='none')

# add legend
module_manager = src.children[0]
module_manager.scalar_lut_manager.show_scalar_bar = True
module_manager.scalar_lut_manager.show_legend = True

# set camera
mlab.view(-65., 60., 14., [1.5, 2., 2.5])

# save the figure
mlab.savefig("figures/particles_001.png")

# run the engine and update the visualisatioin
for i in range(2, 20):
    engine_wrapper.run()
    src.update()
    mlab.savefig("figures/particles_{:03d}.png".format(i))
