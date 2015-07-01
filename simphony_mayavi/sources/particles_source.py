from mayavi.sources.vtk_data_source import VTKDataSource
from traits.api import Dict

from simphony_mayavi.cuds.api import VTKParticles


class ParticlesSource(VTKDataSource):
    """ SimPhoNy CUDS Particle container to Mayavi Source  converter

    """

    #: The mapping from the point uid to the vtk polydata points array.
    point2index = Dict

    #: The mapping from the bond uid to the vtk polydata cell index.
    bond2index = Dict

    @classmethod
    def from_particles(cls, particles):
        """ Return a ParticlesSource from a CUDS Particles container.

        Parameters
        ----------
        particles : Particles
            The CUDS Particles instance to copy the information from.

        """
        if not isinstance(particles, VTKParticles):
            particles = VTKParticles.from_particles(particles)
        data = particles.data_set
        point2index = particles.particle2index
        bond2index = particles.bond2index

        return cls(
            data=data,
            point2index=point2index,
            bond2index=bond2index)
