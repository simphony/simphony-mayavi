from mayavi.sources.vtk_data_source import VTKDataSource
from tvtk.api import tvtk
from traits.api import Dict

from simphony_mayavi.core.api import CUBADataAccumulator
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
        if isinstance(particles, VTKParticles):
            data = particles.data_set
            point2index = particles.particle2index
            bond2index = particles.bond2index
        else:
            points = []
            lines = []
            point2index = {}
            bond2index = {}
            point_data = CUBADataAccumulator()
            bond_data = CUBADataAccumulator()

            for index, point in enumerate(particles.iter_particles()):
                point2index[point.uid] = index
                points.append(point.coordinates)
                point_data.append(point.data)
            for index, bond in enumerate(particles.iter_bonds()):
                bond2index[bond.uid] = index
                lines.append([point2index[uid] for uid in bond.particles])
                bond_data.append(bond.data)

            data = tvtk.PolyData(points=points, lines=lines)
            point_data.load_onto_vtk(data.point_data)
            bond_data.load_onto_vtk(data.cell_data)

        return cls(
            data=data,
            point2index=point2index,
            bond2index=bond2index)
