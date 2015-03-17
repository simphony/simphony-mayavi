from numpy import array
from mayavi.scripts import mayavi2

from simphony.cuds.particles import Particles, Particle, Bond

points = array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]], 'f')
bonds = array([[0, 1], [0, 3], [1, 3, 2]])

container = Particles('test')
uids = [
    container.add_particle(Particle(coordinates=point)) for point in points]
for indices in bonds:
    container.add_bond(Bond(particles=[uids[index] for index in indices]))

# The numpy array data.
temperature = array([10., 20., 30., 40.])


# Now view the data.
@mayavi2.standalone
def view():
    from mayavi.modules.surface import Surface
    from mayavi.modules.glyph import Glyph
    from simphony_mayavi.sources.api import ParticlesSource

    mayavi.new_scene()  # noqa
    src = ParticlesSource.from_particles(container)
    mayavi.add_source(src)  # noqa
    g = Glyph()
    gs = g.glyph.glyph_source
    gs.glyph_source = gs.glyph_dict['sphere_source']
    g.glyph.glyph.scale_factor = 0.05
    s = Surface()

    mayavi.add_module(g)  # noqa
    mayavi.add_module(s)  # noqa

if __name__ == '__main__':
    view()
