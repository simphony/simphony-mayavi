from contextlib import closing

import numpy
from mayavi.scripts import mayavi2

from simphony.core.cuba import CUBA
from simphony.cuds.lattice import (make_hexagonal_lattice,
                                   make_orthorhombic_lattice)
from simphony.io.h5_cuds import H5CUDS

# create some datasets to be saved in a file
hexagonal = make_hexagonal_lattice(
    'hexagonal', 0.1, 0.1, (5, 5, 5), (5, 4, 0))

orthorhombic = make_orthorhombic_lattice(
    'orthorhombic', (0.1, 0.2, 0.3), (5, 5, 5), (5, 4, 0))


def add_temperature(lattice):
    new_nodes = []
    for node in lattice.iter_nodes():
        index = numpy.array(node.index) + 1.0
        node.data[CUBA.TEMPERATURE] = numpy.prod(index)
        new_nodes.append(node)
    lattice.update_nodes(new_nodes)

# add some scalar data (i.e. temperature)
add_temperature(hexagonal)
add_temperature(orthorhombic)

# save the data into cuds.
with closing(H5CUDS.open('lattices.cuds', 'w')) as handle:
    handle.add_dataset(hexagonal)
    handle.add_dataset(orthorhombic)


@mayavi2.standalone
def view():
    from mayavi import mlab
    from mayavi.modules.glyph import Glyph
    from simphony_mayavi.sources.api import CUDSFileSource

    mayavi.new_scene()

    # Mayavi Source
    src = CUDSFileSource()
    src.initialize('lattices.cuds')

    # choose a dataset for display
    src.dataset = 'orthorhombic'

    mayavi.add_source(src)

    # customise the visualisation
    g = Glyph()
    gs = g.glyph.glyph_source
    gs.glyph_source = gs.glyph_dict['sphere_source']
    g.glyph.glyph.scale_factor = 0.05
    g.glyph.scale_mode = 'data_scaling_off'
    mayavi.add_module(g)

    # add legend
    module_manager = src.children[0]
    module_manager.scalar_lut_manager.show_scalar_bar = True
    module_manager.scalar_lut_manager.show_legend = True

    # customise the camera
    mlab.view(63., 38., 3., [5., 4., 0.])


if __name__ == '__main__':
    view()
