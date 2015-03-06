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
        three_d = len(base_vectors) == 3
        if lattice_type in ('Square', 'Cubic', 'Rectangular'):
            if three_d:
                spacing = base_vectors
                origin = origin
                extent = 0, size[0] - 1, 0, size[1] - 1, 0, size[2] - 1
            else:
                spacing = tuple(base_vectors) + (0.0,)
                origin = tuple(origin) + (0.0,)
                extent = 0, size[0] - 1, 0, size[1] - 1, 0, 0
            data = tvtk.ImageData(spacing=spacing, origin=origin)
            data.extent = extent
        elif lattice_type in ('Hexagonal', 'OrthorombicP'):
            raise NotImplementedError()
        return cls(data=data)
