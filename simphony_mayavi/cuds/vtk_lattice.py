from __future__ import division
from itertools import izip

import numpy
from tvtk.api import tvtk
from simphony.cuds.abc_lattice import ABCLattice
from simphony.cuds.lattice import LatticeNode
from simphony.cuds.primitive_cell import BravaisLattice, PrimitiveCell
from simphony.core.cuds_item import CUDSItem
from simphony.core.data_container import DataContainer

from simphony_mayavi.core.api import CubaData, supported_cuba, mergedocs
from simphony_mayavi.core.api import CUBADataAccumulator

from .lattice_tools import (vector_len, guess_primitive_vectors,
                            find_lattice_type)

VTK_POLY_LINE = 4


@mergedocs(ABCLattice)
class VTKLattice(ABCLattice):

    def __init__(self, name, primitive_cell, data_set, data=None):
        """ Constructor.

        Parameters
        ----------
        name : string
            The name of the container.

        primitive_cell : PrimitiveCell
            primitive cell specifying the 3D Bravais lattice

        data_set : tvtk.DataSet
            The dataset to wrap in the CUDS api. If it is a tvtk.PolyData, the
            points are assumed to be arranged in C-contiguous order so that
            the first point is the origin and the last point is furthest away
            from the origin

        data : DataContainer
            The data attribute to attach to the container. Default is None.
        """
        self.name = name
        self._primitive_cell = primitive_cell
        self._data = DataContainer() if data is None else DataContainer(data)
        self.data_set = data_set

        self._items_count = {
            CUDSItem.NODE: lambda: self.size
            }

        #: The currently supported and stored CUBA keywords.
        self.supported_cuba = supported_cuba()

        # For constructing CubaData
        data = data_set.point_data
        npoints = data_set.number_of_points
        if data.number_of_arrays == 0 and npoints != 0:
            size = npoints
        else:
            size = None
        #: Easy access to the vtk PointData structure
        self.point_data = CubaData(
            data, stored_cuba=self.supported_cuba, size=size)

        # Determine origin
        try:
            self._origin = self.data_set.origin
        except AttributeError:
            self._origin = self.data_set.points.get_point(0)

        # Estimate the lattice size
        if isinstance(self.data_set, tvtk.ImageData):
            extent = self.data_set.extent
            x_size = extent[1] - extent[0] + 1
            y_size = extent[3] - extent[2] + 1
            z_size = extent[5] - extent[4] + 1
            self._size = x_size, y_size, z_size
        elif isinstance(self.data_set, tvtk.PolyData):
            # Assumed the last point is the furthest point from origin
            # alternative method is to calculate distances for each point
            # but this maybe costly for large datasets
            p_last = data_set.get_point(npoints-1) - numpy.array(self.origin)
            # primitive cell can be used to deduce the size
            pcs = numpy.array((primitive_cell.p1,
                               primitive_cell.p2,
                               primitive_cell.p3), dtype='double')
            # compute the inverse
            dims = numpy.round(numpy.inner(p_last, numpy.linalg.inv(pcs))+1)
            self._size = tuple(dims.astype("int"))
        else:
            message = ("Expect data_set to be either tvtk.ImageData "
                       "or tvtk.PolyData, got {}")
            raise TypeError(message.format(type(self.data_set)))

    @property
    def data(self):
        """ The container data
        """
        return DataContainer(self._data)

    @data.setter
    def data(self, value):
        self._data = DataContainer(value)

    @property
    def size(self):
        return self._size

    @property
    def origin(self):
        return self._origin

    @property
    def primitive_cell(self):
        return self._primitive_cell

    # Node operations ########################################################

    def get_node(self, index):
        point_id = self._get_point_id(index)
        return LatticeNode(index, data=self.point_data[point_id])

    def update_nodes(self, nodes):
        """Update the corresponding lattice nodes (data copied).

        Parameters
        ----------
        nodes : iterable of LatticeNode objects
            reference to LatticeNode objects from where the data is
            copied to the Lattice

        """
        for node in nodes:
            point_id = self._get_point_id(node.index)
            self.point_data[point_id] = node.data

    def iter_nodes(self, indices=None):
        """Get an iterator over the LatticeNodes described by the indices.

        Parameters
        ----------
        indices : iterable set of int[3], optional
            When indices (i.e. node index coordinates) are provided, then
            nodes are returned in the same order of the provided indices.
            If indices is None, there is no restriction on the order the
            nodes that are returned.

        Returns
        -------
        A generator for LatticeNode objects
        """
        if indices is None:
            for index in numpy.ndindex(*self.size):
                yield self.get_node(index)
        else:
            for index in indices:
                yield self.get_node(index)

    def count_of(self, item_type):
        """ Return the count of item_type in the container.

        Parameters
        ----------
        item_type : CUDSItem
            The CUDSItem enum of the type of the items to return
            the count of.

        Returns
        -------
        count : int
            The number of items of item_type in the container.

        Raises
        ------
        ValueError :
            If the type of the item is not supported in the current
            container.

        """
        try:
            return numpy.prod(self._items_count[item_type]())
        except KeyError:
            error_str = "Trying to obtain count of non-supported item: {}"
            raise ValueError(error_str.format(item_type))

    def get_coordinate(self, index):
        ''' Return the (x, y, z) coordinates of a node at ``index``

        Parameters
        ----------
        index : tuple of int[3]

        Returns
        -------
        coordinates : tuple of float[3]
        '''
        point_id = self._get_point_id(index)
        return self.data_set.get_point(point_id)

    # Alternative constructors ###############################################

    @classmethod
    def empty(cls, name, primitive_cell, size, origin, data=None):
        """ Create a new empty Lattice.

        """
        bravais_lattice = primitive_cell.bravais_lattice
        if bravais_lattice in (BravaisLattice.CUBIC, BravaisLattice.TETRAGONAL,
                               BravaisLattice.ORTHORHOMBIC):
            # Compute the spacing from the primitive cell
            spacing = tuple(vector_len(p) for p in (primitive_cell.p1,
                                                    primitive_cell.p2,
                                                    primitive_cell.p3))
            data_set = tvtk.ImageData(spacing=spacing, origin=origin)
            data_set.extent = 0, size[0] - 1, 0, size[1] - 1, 0, size[2] - 1
        elif bravais_lattice in BravaisLattice:
            y, z, x = numpy.meshgrid(
                range(size[1]), range(size[2]), range(size[0]))
            points = numpy.zeros(shape=(x.size, 3), dtype='double')
            # construct points using primitive cells
            for idim in range(3):
                points[:, idim] += primitive_cell.p1[idim]*x.ravel() +\
                    primitive_cell.p2[idim]*y.ravel() +\
                    primitive_cell.p3[idim]*z.ravel()
                points[:, idim] += origin[idim]
            data_set = tvtk.PolyData(points=points)
        else:
            message = 'Unknown lattice type: {}'
            raise ValueError(message.format(str(bravais_lattice)))

        return cls(name=name, primitive_cell=primitive_cell,
                   data=data, data_set=data_set)

    @classmethod
    def from_lattice(cls, lattice):
        """ Create a new Lattice from the provided one.

        """
        origin = lattice.origin
        primitive_cell = lattice.primitive_cell
        lattice_type = primitive_cell.bravais_lattice
        size = lattice.size
        name = lattice.name
        node_data = CUBADataAccumulator()
        data = lattice.data

        if lattice_type in (
                BravaisLattice.CUBIC, BravaisLattice.TETRAGONAL,
                BravaisLattice.ORTHORHOMBIC):
            # Compute the spacing from the primitive cell
            spacing = tuple(map(vector_len, (primitive_cell.p1,
                                             primitive_cell.p2,
                                             primitive_cell.p3)))
            origin = origin
            data_set = tvtk.ImageData(spacing=spacing, origin=origin)
            data_set.extent = 0, size[0] - 1, 0, size[1] - 1, 0, size[2] - 1
            # vtk ravels the point positions in a very weird way
            # this setup has been supported by tests.
            y, z, x = numpy.meshgrid(
                range(size[1]), range(size[2]), range(size[0]))
            indices = izip(x.ravel(), y.ravel(), z.ravel())
        elif lattice_type in BravaisLattice:
            y, z, x = numpy.meshgrid(
                range(size[1]), range(size[2]), range(size[0]))
            points = numpy.zeros(shape=(x.size, 3), dtype='double')

            # construct points using primitive cells
            for idim in range(3):
                points[:, idim] += primitive_cell.p1[idim]*x.ravel() +\
                    primitive_cell.p2[idim]*y.ravel() +\
                    primitive_cell.p3[idim]*z.ravel()
                points[:, idim] += origin[idim]

            data_set = tvtk.PolyData(points=points)
            indices = izip(x.ravel(), y.ravel(), z.ravel())
        else:
            message = 'Unknown lattice type: {}'.format(lattice_type)
            raise ValueError(message)

        for node in lattice.iter_nodes(indices):
            node_data.append(node.data)
        node_data.load_onto_vtk(data_set.point_data)

        return cls(name=name, primitive_cell=primitive_cell, data=data,
                   data_set=data_set)

    @classmethod
    def from_dataset(cls, name, data_set, data=None):
        """ Create a new Lattice and try to guess the ``primitive_cell``

        Parameters
        ----------
        name : str

        data_set : tvtk.ImageData or tvtk.PolyData
            The dataset to wrap in the CUDS api.  If it is a PolyData,
            the points are assumed to be arranged in C-contiguous order

        data : DataContainer
            The data attribute to attach to the container. Default is None.

        Returns
        -------
        lattice : VTKLattice

        Raises
        ------
        TypeError :
            If data_set is not either tvtk.ImageData or tvtk.PolyData

        IndexError:
            If the lattice nodes are not arranged in C-contiguous order
        """
        if isinstance(data_set, tvtk.ImageData):
            spacing = data_set.spacing
            unique_spacing = numpy.unique(spacing)
            if len(unique_spacing) == 1:
                primitive_cell = PrimitiveCell.for_cubic_lattice(spacing[0])
            elif len(unique_spacing) == 2:
                a, c = unique_spacing
                if sum(spacing == a) == 2:
                    primitive_cell = PrimitiveCell.for_tetragonal_lattice(a, c)
                else:
                    primitive_cell = PrimitiveCell.for_tetragonal_lattice(c, a)
            else:
                factory = PrimitiveCell.for_orthorhombic_lattice
                primitive_cell = factory(*spacing)

            return cls(name=name, primitive_cell=primitive_cell,
                       data=data, data_set=data_set)

        if not isinstance(data_set, tvtk.PolyData):
            # Not ImageData nor PolyData
            message = 'Cannot convert {} to a cuds Lattice'
            raise TypeError(message.format(type(data_set)))

        # data_set is an instance of tvtk.PolyData
        points = data_set.points.to_array()

        # Assumed C-contiguous order of points
        p1, p2, p3 = guess_primitive_vectors(points)

        # This will raise a TypeError if no bravais lattice type matches
        bravais_lattice = find_lattice_type(p1, p2, p3)

        primitive_cell = PrimitiveCell(p1, p2, p3, bravais_lattice)

        return cls(name=name, primitive_cell=primitive_cell,
                   data=data, data_set=data_set)

    # Private methods ######################################################

    def _get_point_id(self, index):
        """ Return a raveled index for a given indices in the lattice

        Parameters
        ----------
        index : int[3]

        Returns
        -------
        index : int
        """
        try:
            point_id = self.data_set.compute_point_id(index)
        except AttributeError:
            point_id = int(
                numpy.ravel_multi_index(index, self.size, order="F"))
        if point_id < 0:
            raise IndexError('index:{} is out of range'.format(index))
        return point_id
