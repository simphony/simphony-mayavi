from mayavi.sources.vtk_data_source import VTKDataSource
from tvtk.api import tvtk
from traits.api import Dict


class ParticlesSource(VTKDataSource):
    """ A Mayavi Source wrapping a SImphony CUDS Particle container.

    """

    #: The mapping from the point uid to the vtk polydata points array.
    point2index = Dict

    #: The mapping from the bond uid to the vtk polydata cell index.
    bond2index = Dict

    @classmethod
    def from_particles(cls, particles):
        points = []
        lines = []
        point2index = {}
        bond2index = {}
        for index, point in enumerate(particles.iter_particles()):
            point2index[point.uid] = index
            points.append(point.coordinates)
        for index, bond in enumerate(particles.iter_bonds()):
            bond2index[bond.uid] = index
            lines.append([point2index[uid] for uid in bond.particles])

        data = tvtk.PolyData(points=points, lines=lines)
        return cls(
            data=data,
            point2index=point2index,
            bond2index=bond2index)


def cell_array_slicer(data):
    count = 0
    collection = []
    for value in data:
        if count == 0:
            collection = []
            count = value
        else:
            collection.append(value)
            count -= 1
            if count == 0:
                yield collection
