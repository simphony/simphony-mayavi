from mayavi.sources.vtk_data_source import VTKDataSource
from tvtk.api import tvtk
from traits.api import Dict

from .cuds_data_accumulator import CUDSDataAccumulator


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
        points = []
        lines = []
        point2index = {}
        bond2index = {}
        point_data = CUDSDataAccumulator()
        bond_data = CUDSDataAccumulator()

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
