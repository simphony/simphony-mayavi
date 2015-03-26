from numpy import array

from simphony.cuds.particles import Particles, Particle, Bond
from simphony.core.data_container import DataContainer

points = array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]], 'f')
bonds = array([[0, 1], [0, 3], [1, 3, 2]])
temperature = array([10., 20., 30., 40.])

particles = Particles('test')
uids = []
for index, point in enumerate(points):
    uid = particles.add_particle(
        Particle(
            coordinates=point,
            data=DataContainer(TEMPERATURE=temperature[index])))
    uids.append(uid)

for indices in bonds:
    particles.add_bond(Bond(particles=[uids[index] for index in indices]))


if __name__ == '__main__':
    from simphony.visualisation import mayavi_tools

    # Visualise the Particles object
    mayavi_tools.show(particles)
