from collections import MutableSequence

import numpy
from tvtk.api import tvtk


# FIXME This is a good candidate class for mayavi.


class CellCollection(MutableSequence):
    """ A mutable sequence of cells rapping a tvtk.CellArray.

    """

    def __init__(self, cell_array=None):
        """ Constructor

        Parameters
        ----------
        cell_array : tvtk.CellArray
            The tvtk object to wrap. Default value is an empty
            tvtk.CellArray.

        """
        if cell_array is None:
            cell_array = tvtk.CellArray()
        self._cell_array = cell_array

    def __len__(self):
        """ The number of contained cells.

        """
        # Need to use the vtk implementation due to issue
        # https://github.com/enthought/mayavi/issues/178
        vtk_object = tvtk.to_vtk(self._cell_array)
        return vtk_object.GetNumberOfCells()

    def __getitem__(self, index):
        """ Return the connectivity list for the cell at ``index``.

        """
        location = self._cell_location(index)
        points = tvtk.IdList()
        self._cell_array.get_cell(location, points)
        return tuple(points)

    def __setitem__(self, index, value):
        """ Update the connectivity list for cell at ``index``.

        .. note::

           If the size of the connectivity list changes a slower
           path creating temporary arrays is used.


        """
        length = len(self)
        if 0 <= index < length:
            cells = self._cell_array
            location = self._cell_location(index)
            data = cells.data
            npoints = data[location]
            start = location + 1
            if npoints == len(value):
                for i, j in enumerate(value):
                    data[start + i] = j
            else:
                array = cells.to_array()
                left, cell, right = numpy.split(
                    array, [location, start + npoints])
                new_cell = numpy.array([len(value)] + value, left.dtype)
                array = numpy.r_[left, new_cell, right]
                cells.set_cells(length, array)
        else:
            raise IndexError('{} is out of index range'.format(index))

    def __delitem__(self, index):
        """ Remove cell at ``index``.

        .. note::

           This operation will need to create temporary arrays in order
           to keep the data info consistent.


        """
        length = len(self)
        cells = self._cell_array
        location = self._cell_location(index)
        npoints = cells.data[location]
        start = location + 1
        if 0 <= index < length:
            array = cells.to_array()
            left, cell, right = numpy.split(
                array, [location, start + npoints])
            array = numpy.r_[left, right]
            cells.set_cells(length - 1, array)
        else:
            raise IndexError('{} is out of index range'.format(index))

    def insert(self, index, value):
        """ Insert cell at ``index``.

        .. note::

           This operation needs to use a slower path based on temporary
           array when index < sequence length.

        """
        length = len(self)
        cells = self._cell_array
        if 0 <= index < length:
            location = self._cell_location(index)
            array = cells.to_array()
            left, right = numpy.split(
                array, (location,))
            new_cell = numpy.array([len(value)] + value, left.dtype)
            array = numpy.r_[left, new_cell, right]
            cells.set_cells(length + 1, array)
        elif index >= length:
            cells.insert_next_cell(value)
        else:
            raise IndexError('{} is out of index range'.format(index))

    # Private methods ######################################################

    def _add_arrays(self, arrays):
        data = self._data
        for cuba, array in arrays:
            array_id = data.add_array(array)
            data.get_array(array_id).name = cuba.name

    def _cell_location(self, index):
        data = self._cell_array.data
        location = 0
        for _ in range(index):
            location += int(data[location]) + 1
        if location == len(data):
            raise IndexError("Index {} out of range".format(index))
        return location
