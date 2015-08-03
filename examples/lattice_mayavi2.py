import numpy

from mayavi.scripts import mayavi2
from simphony.cuds.lattice import (
    make_hexagonal_lattice, make_cubic_lattice, make_square_lattice)
from simphony.core.cuba import CUBA

hexagonal = make_hexagonal_lattice('test', 0.1, (5, 4))
square = make_square_lattice('test', 0.1, (5, 4))
cubic = make_cubic_lattice('test', 0.1, (5, 10, 12))


def add_temperature(lattice):
    for node in lattice.iter_nodes():
        index = numpy.array(node.index) + 1.0
        node.data[CUBA.TEMPERATURE] = numpy.prod(index)
        lattice.update_node(node)

add_temperature(hexagonal)
add_temperature(cubic)
add_temperature(square)


# Now view the data.
@mayavi2.standalone
def view(lattice):
    from mayavi.modules.glyph import Glyph
    from simphony_mayavi.sources.api import CUDSSource
    mayavi.new_scene()  # noqa
    src = CUDSSource(cuds=lattice)
    mayavi.add_source(src)  # noqa
    g = Glyph()
    gs = g.glyph.glyph_source
    gs.glyph_source = gs.glyph_dict['sphere_source']
    g.glyph.glyph.scale_factor = 0.02
    g.glyph.scale_mode = 'data_scaling_off'
    mayavi.add_module(g)  # noqa

if __name__ == '__main__':
    view(cubic)
