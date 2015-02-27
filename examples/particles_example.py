from numpy import array
from tvtk.api import tvtk
from mayavi.scripts import mayavi2

from simphony.cuds.particles import ParticleContainer, Particle, Bond

points = array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]], 'f')
bonds = array([[0, 1], [0, 3], [1, 3, 2]])

container = ParticleContainer('test')
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
    from simphony.visualization import mayavi_tools as tools

    mayavi.new_scene()
    src = tools.ParticleSource.from_particles(container)
    mayavi.add_source(src)
    g = Glyph()
    s = Surface()

    mayavi.add_module(g)
    mayavi.add_module(s)

if __name__ == '__main__':
    view()
