from numpy import array

from simphony.core.data_container import DataContainer
from simphony.cuds.particles import Particle, Bond
from simphony.visualisation import mayavi_tools

points = array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]], 'f')
bonds = array([[0, 1], [0, 3], [1, 3, 2]])
temperature = array([10., 20., 30., 40.])

particles = mayavi_tools.VTKParticles('test')

# add particles
particle_iter = (Particle(coordinates=point,
                          data=DataContainer(TEMPERATURE=temperature[index]))
                 for index, point in enumerate(points))
uids = particles.add(particle_iter)

# add bonds
bond_iter = (Bond(particles=[uids[index] for index in indices])
             for indices in bonds)
particles.add(bond_iter)

if __name__ == '__main__':

    # Visualise the Particles object
    mayavi_tools.show(particles)
