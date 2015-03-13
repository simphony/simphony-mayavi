from mayavi.scripts import mayavi2

from simphony.cuds.lattice import make_hexagonal_lattice


lattice = make_hexagonal_lattice('test', 0.1, (5, 4))


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
    g.glyph.glyph.scale_factor = 0.05
    mayavi.add_module(g)  # noqa

if __name__ == '__main__':
    view()