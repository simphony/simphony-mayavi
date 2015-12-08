from numpy import array
from mayavi.scripts import mayavi2

from simphony.cuds.particles import Particles, Particle, Bond
from simphony.core.data_container import DataContainer

points = array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]], 'f')
bonds = array([[0, 1], [0, 3], [1, 3, 2]])
temperature = array([10., 20., 30., 40.])

container = Particles('test')

# add particles
particle_iter = (Particle(coordinates=point,
                          data=DataContainer(TEMPERATURE=temperature[index]))
                 for index, point in enumerate(points))
uids = container.add_particles(particle_iter)

# add bonds
bond_iter = (Bond(particles=[uids[index] for index in indices])
             for indices in bonds)
container.add_bonds(bond_iter)


# Now view the data.
@mayavi2.standalone
def view():
    from mayavi.modules.surface import Surface
    from mayavi.modules.glyph import Glyph
    from simphony_mayavi.sources.api import CUDSSource

    mayavi.new_scene()  # noqa
    src = CUDSSource(cuds=container)
    mayavi.add_source(src)  # noqa
    g = Glyph()
    gs = g.glyph.glyph_source
    gs.glyph_source = gs.glyph_dict['sphere_source']
    g.glyph.glyph.scale_factor = 0.05
    g.glyph.scale_mode = 'data_scaling_off'
    s = Surface()
    s.actor.mapper.scalar_visibility = False

    mayavi.add_module(g)  # noqa
    mayavi.add_module(s)  # noqa

if __name__ == '__main__':
    view()
