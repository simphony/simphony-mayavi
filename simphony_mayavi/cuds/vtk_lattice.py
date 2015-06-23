from __future__ import division
from itertools import izip

import numpy
from tvtk.api import tvtk
from simphony.cuds.abstractlattice import ABCLattice
from simphony.cuds.lattice import LatticeNode
from simphony.core.data_container import DataContainer

from simphony_mayavi.core.api import CubaData, supported_cuba, mergedocs
from simphony_mayavi.core.api import CUBADataAccumulator


VTK_POLY_LINE = 4


@mergedocs(ABCLattice)
class VTKLattice(ABCLattice):

    def __init__(self, name, type_, data=None, data_set=None):
        self.name = name
        self._data = DataContainer() if data is None else DataContainer(data)
        self._type = type_
        self.data_set = data_set

        #: The currently supported and stored CUBA keywords.
        self.supported_cuba = supported_cuba()

        data = data_set.point_data
        npoints = data_set.number_of_points
        if data.number_of_arrays == 0 and npoints != 0:
            size = npoints
        else:
            size = None
        #: Easy access to the vtk PointData structure
        self.point_data = CubaData(
            data, stored_cuba=self.supported_cuba, size=size)

        # Estimate the lattice parameters
        if self.type in ('Cubic', 'OrthorombicP', 'Square', 'Rectangular'):
            extend = self.data_set.extent
            x_size = extend[1] - extend[0] + 1
            y_size = extend[3] - extend[2] + 1
            z_size = extend[5] - extend[4] + 1
            self._origin = self.data_set.origin
            self._base_vector = self.data_set.spacing
        elif self.type == 'Hexagonal':
            # FIXME: we assume a lattice on the xy plane
            points = self.data_set.points.to_array()
            x_size = len(numpy.unique(points[:, 0])) // 2 - 1
            y_size = len(numpy.unique(points[:, 1]))
            z_size = len(numpy.unique(points[:, 2]))
            self._origin = tuple(points[0])
            self._base_vector = (
                points[1, 0] - points[0, 0],
                points[x_size, 1] - points[0, 1],
                0.0)
        else:
            message = 'Unknown lattice type: {}'.format(self.type)
            raise ValueError(message)
        self._size = x_size, y_size, z_size

    @property
    def data(self):
        """ The container data
        """
        return DataContainer(self._data)

    @data.setter
    def data(self, value):
        self._data = DataContainer(value)

    @property
    def type(self):
        return self._type

    @property
    def size(self):
        return self._size

    @property
    def origin(self):
        return self._origin

    @property
    def base_vect(self):
        return self._base_vector

    # Node operations ########################################################

    def get_node(self, index):
        point_id = self._get_point_id(index)
        return LatticeNode(index, data=self.point_data[point_id])

    def update_node(self, node):
        point_id = self._get_point_id(node.index)
        self.point_data[point_id] = node.data

    def iter_nodes(self, indices=None):
        if indices is None:
            for index in numpy.ndindex(*self.size):
                yield self.get_node(index)
        else:
            for index in indices:
                yield self.get_node(index)

    def get_coordinate(self, index):
        point_id = self._get_point_id(index)
        return self.data_set.get_point(point_id)

    # Alternative constructors ###############################################

    @classmethod
    def empty(cls, name, type_, base_vector, size, origin, data=None):
        if type_ in ('Cubic', 'OrthorombicP', 'Square', 'Rectangular'):
            data_set = tvtk.ImageData(spacing=base_vector, origin=origin)
            data_set.extent = 0, size[0] - 1, 0, size[1] - 1, 0, size[2] - 1
        elif type_ == 'Hexagonal':
            x, y, z = numpy.meshgrid(
                range(size[0]), range(size[1]), range(size[2]))
            points = numpy.zeros(shape=(x.size, 3), dtype='double')
            points[:, 0] += base_vector[0] * x.ravel() \
                + 0.5 * base_vector[0] * y.ravel()
            points[:, 1] += base_vector[1] * y.ravel()
            points[:, 0] += origin[0]
            points[:, 1] += origin[1]
            points[:, 2] += origin[2]
            data_set = tvtk.PolyData(points=points)
        else:
            message = 'Unknown lattice type: {}'.format(type_)
            raise ValueError(message)
        return cls(name=name, type_=type_, data=data, data_set=data_set)

    @classmethod
    def from_lattice(cls, lattice):

        base_vectors = lattice.base_vect
        origin = lattice.origin
        lattice_type = lattice.type
        size = lattice.size
        name = lattice.name
        node_data = CUBADataAccumulator()
        data = lattice.data

        if lattice_type in (
                'Cubic', 'OrthorombicP', 'Square', 'Rectangular'):
            spacing = base_vectors
            origin = origin
            data_set = tvtk.ImageData(spacing=spacing, origin=origin)
            data_set.extent = 0, size[0] - 1, 0, size[1] - 1, 0, size[2] - 1
            # vtk ravels the point positions in a very weird way
            # this setup has been supported by tests.
            y, z, x = numpy.meshgrid(
                range(size[1]), range(size[2]), range(size[0]))
            indices = izip(x.ravel(), y.ravel(), z.ravel())
        elif lattice_type == 'Hexagonal':
            x, y, z = numpy.meshgrid(
                range(size[0]), range(size[1]), range(size[2]))
            points = numpy.zeros(shape=(x.size, 3), dtype='double')
            points[:, 0] += base_vectors[0] * x.ravel() \
                + 0.5 * base_vectors[0] * y.ravel()
            points[:, 1] += base_vectors[1] * y.ravel()
            points[:, 0] += origin[0]
            points[:, 1] += origin[1]
            points[:, 2] += origin[2]
            data_set = tvtk.PolyData(points=points)
            indices = izip(x.ravel(), y.ravel(), z.ravel())
        else:
            message = 'Unknown lattice type: {}'.format(lattice_type)
            raise ValueError(message)

        for node in lattice.iter_nodes(indices):
            node_data.append(node.data)
        node_data.load_onto_vtk(data_set.point_data)

        return cls(name=name, type_=lattice_type, data=data, data_set=data_set)

    # Private methods ######################################################

    def _get_point_id(self, index):
        if self.type == 'Hexagonal':
            point_id = int(
                numpy.ravel_multi_index(index, self.size, order='F'))
        else:
            point_id = self.data_set.compute_point_id(index)
        if point_id < 0:
            raise IndexError('index:{} is out of range'.format(index))
        return point_id
