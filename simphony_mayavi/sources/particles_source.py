from mayavi.sources.vtk_data_source import VTKDataSource
from tvtk.api import tvtk


class ParticleSource(VTKDataSource):



    @classmethod
    def from_particles(cls, particles):
        points = []
        ids = {}
        lines = []
        for index, point in enumerate(particles.iter_particles()):
            points.append(point.coordinates)
            ids[point.uid] = index
        for bond in particles.iter_bonds():
            lines.append([ids[uid] for uid in bond.particles])
        data = tvtk.PolyData(points=points, lines=lines)
        return cls(data=data, )
