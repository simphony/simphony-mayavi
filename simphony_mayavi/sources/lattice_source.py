from itertools import izip

import numpy

from mayavi.sources.vtk_data_source import VTKDataSource
from tvtk.api import tvtk

from .cuds_data_accumulator import CUDSDataAccumulator


class LatticeSource(VTKDataSource):
    """ A Mayavi Source wrapping a SimPhoNy CUDS Particle container.


    """

    @classmethod
    def from_lattice(cls, lattice):
        base_vectors = lattice.base_vect
        origin = lattice.origin
        lattice_type = lattice.type
        size = lattice.size
        node_data = CUDSDataAccumulator()

        if lattice_type in ('Square', 'Rectangular'):
            spacing = tuple(base_vectors) + (0.0,)
            origin = tuple(origin) + (0.0,)
            data = tvtk.ImageData(spacing=spacing, origin=origin)
            data.extent = 0, size[0] - 1, 0, size[1] - 1, 0, 0
            x, y = numpy.meshgrid(range(size[0]), range(size[1]))
            indices = izip(x.ravel(), y.ravel())

        elif lattice_type in ('Cubic', 'OrthorombicP'):
            spacing = base_vectors
            origin = origin
            data = tvtk.ImageData(spacing=spacing, origin=origin)
            data.extent = 0, size[0] - 1, 0, size[1] - 1, 0, size[2] - 1
            # vtk ravels the point positions in a very weird way
            # this setup has been supported by tests.
            y, z, x = numpy.meshgrid(
                range(size[1]), range(size[2]), range(size[0]))
            indices = izip(x.ravel(), y.ravel(), z.ravel())

        elif lattice_type == 'Hexagonal':
            x, y = numpy.meshgrid(range(size[0]), range(size[1]))
            points = numpy.zeros(shape=(x.size, 3), dtype='double')
            points[:, 0] += base_vectors[0] * x.ravel() \
                + 0.5 * base_vectors[0] * (y.ravel() % 2)
            points[:, 1] += base_vectors[1] * y.ravel()
            points[:, 0] += origin[0]
            points[:, 1] += origin[1]
            data = tvtk.PolyData(points=points)
            indices = izip(x.ravel(), y.ravel())

        else:
            message = 'Unknown lattice type: {}'.format(lattice_type)
            raise ValueError(message)

        for node in lattice.iter_nodes(indices):
            node_data.append(node.data)
        node_data.load_onto_vtk(data.point_data)

        return cls(data=data)
