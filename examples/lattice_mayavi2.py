import numpy

from mayavi.scripts import mayavi2
from simphony.cuds.lattice import (
    make_hexagonal_lattice, make_cubic_lattice,
    make_face_centered_cubic_lattice,
    make_body_centered_cubic_lattice)
from simphony.core.cuba import CUBA

hexagonal = make_hexagonal_lattice(
    'hexagonal', 0.1, 0.05, (5, 10, 12), (5, 4, 0))
cubic = make_cubic_lattice("cubic", 0.1, (5, 10, 12), (5, 4, 0))
fcc = make_face_centered_cubic_lattice(
    'fcc', 0.1, (5, 10, 12), (5, 4, 0))
bcc = make_body_centered_cubic_lattice(
    'bcc', 0.1, (5, 10, 12), (5, 4, 0))



def add_temperature(lattice):
    new_nodes = []
    for node in lattice.iter_nodes():
        index = numpy.array(node.index) + 1.0
        node.data[CUBA.TEMPERATURE] = numpy.prod(index)
        new_nodes.append(node)
    lattice.update_nodes(new_nodes)

add_temperature(hexagonal)
add_temperature(cubic)
add_temperature(bcc)
add_temperature(fcc)



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
    # view(hexagonal)
    view(cubic)
    # view(fcc)
    # view(bcc)
