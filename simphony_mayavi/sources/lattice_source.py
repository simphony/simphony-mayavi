import numpy

from mayavi.sources.vtk_data_source import VTKDataSource
from tvtk.api import tvtk


class LatticeSource(VTKDataSource):
    """ A Mayavi Source wrapping a SimPhoNy CUDS Particle container.

    """

    @classmethod
    def from_lattice(cls, lattice):
        base_vectors = lattice.base_vect
        origin = lattice.origin
        lattice_type = lattice.type
        size = lattice.size
        if lattice_type in ('Square', 'Rectangular'):
            spacing = tuple(base_vectors) + (0.0,)
            origin = tuple(origin) + (0.0,)
            data = tvtk.ImageData(spacing=spacing, origin=origin)
            data.extent = 0, size[0] - 1, 0, size[1] - 1, 0, 0
        elif lattice_type == ('Cubic', 'OrthorombicP'):
            spacing = base_vectors
            origin = origin
            data = tvtk.ImageData(spacing=spacing, origin=origin)
            data.extent = 0, size[0] - 1, 0, size[1] - 1, 0, size[2] - 1
        elif lattice_type == 'Hexagonal':
            points = numpy.mgrid[:size[0], :size[1], :1].astype('float')
            points[0] *= base_vectors[0]
            points[0, :, ::2] += 0.5 * base_vectors[0]
            points[0] += origin[0]
            points[1] *= base_vectors[1]
            points[1] += origin[1]
            data = tvtk.PolyData(points=points.T.reshape(numpy.prod(size), 3))
        else:
            message = 'Unknown lattice type: {}'.format(lattice_type)
            raise ValueError(message)
        return cls(data=data)
