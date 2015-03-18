from mayavi.scripts import mayavi2

from simphony.cuds.lattice import make_hexagonal_lattice
from simphony.core.cuba import CUBA

lattice = make_hexagonal_lattice('test', 0.1, (5, 4))

temperature = 0.2
for node in lattice.iter_nodes():
    node.data[CUBA.TEMPERATURE] = temperature
    lattice.update_node(node)
    temperature += 0.2

# Now view the data.
@mayavi2.standalone
def view():
    from mayavi.modules.glyph import Glyph
    from simphony_mayavi.sources.api import LatticeSource

    mayavi.new_scene()  # noqa
    src = LatticeSource.from_lattice(lattice)
    mayavi.add_source(src)  # noqa
    g = Glyph()
    gs = g.glyph.glyph_source
    gs.glyph_source = gs.glyph_dict['sphere_source']
    g.glyph.glyph.scale_factor = 0.02
    g.glyph.scale_mode = 'data_scaling_off'
    mayavi.add_module(g)  # noqa

if __name__ == '__main__':
    view()
