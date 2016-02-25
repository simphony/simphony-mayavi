from mayavi.scripts import mayavi2
from simphony_mayavi.sources.tests.testing_utils import DummyEngine

# Comply to SimPhoNy modeling engine API
engine_wrapper = DummyEngine()


@mayavi2.standalone
def view():
    from mayavi.modules.glyph import Glyph
    from simphony_mayavi.sources.api import EngineSource
    from mayavi import mlab

    # Define EngineSource, choose dataset
    src = EngineSource(engine=engine_wrapper,
                       dataset="particles")

    # choose the CUBA attribute for display
    src.point_scalars_name = "TEMPERATURE"

    mayavi.add_source(src)

    # customise the visualisation
    g = Glyph()
    gs = g.glyph.glyph_source
    gs.glyph_source = gs.glyph_dict['sphere_source']
    g.glyph.glyph.scale_factor = 0.2
    g.glyph.scale_mode = 'data_scaling_off'
    mayavi.add_module(g)

    # add legend
    module_manager = src.children[0]
    module_manager.scalar_lut_manager.show_scalar_bar = True
    module_manager.scalar_lut_manager.show_legend = True

    # set camera
    mlab.view(-65., 60., 14., [1.5, 2., 2.5])


if __name__ == '__main__':
    view()
