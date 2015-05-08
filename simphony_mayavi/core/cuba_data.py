from collections import MutableSequence

import numpy
from tvtk.api import tvtk
from enum import Enum
from simphony.core.cuba import CUBA
from simphony.core.data_container import DataContainer

from .utils import CUBAWorks


class AttributeSetType(Enum):
    """ Enum to the supported DatasetAttribute types.

    """
    POINTS = 1
    CELLS = 2

MASKED = "{}-mask"


class CubaData(MutableSequence):
    """ Map a vtkCellData or vtkPointData object to a sequence of DataContainers.

    The class implements the :class:`MutableSequence` api to wrap a
    :class:`tvtk.CellData` or :class:`tvtk.PointData` array where each
    CUBA key is a :class:`tvtk.DataArray`. The aim is to help the
    conversion between column based structure of the
    :class:`vtkCellData` or :class:`vtkPointData` and the row based
    access provided by a list of
    :class:`~.DataContainer<DataContainers>`.

    .. note::

       Missing values for the attribute arrays are stored in separate
       attribute arrays named "<CUBA.name>-mask" as ``0`` while
       present values are designated with a ``1``.

    """

    def __init__(self, attribute_data, cuba_works=None):
        """ Constructor

        Parameters
        ----------
        attribute_data: tvtk.DataSetAttributes
            The vtk attribute container.
        cuba_works : CUBAWorks
            A CUBA keys helper to define and manage the
            supported CUBA keys. The default value is
            using the :meth:`~.CUBAWorks.default`
            class method.

        """
        self._data = attribute_data
        if cuba_works is None:
            cuba_works = CUBAWorks.default()
        self._cuba_works = cuba_works

    @property
    def cubas(self):
        """ The set of currently stored CUBA keys.

        For each cuba key there is an associated
        :class:`~.DataArray` connected to the :class:`~.PointData`
        or :class:`~.CellData`

        """
        data = self._data
        n = data.number_of_arrays
        return {CUBA[data.get_array(index).name] for index in range(0, n, 2)}

    def __len__(self):
        """ The number of rows (i.e. DataContainers) stored.
        """
        data = self._data
        if data.number_of_arrays == 0:
            return 0
        else:
            return len(data.get_array(0))

    def __setitem__(self, index, value):
        """Store the DataContainer at ``index``.

        If the provided value contains new, but supported, CUBA keys
        then a new empty array is created for them and updated with
        the associated values of ``value``.  Unsupported CUBA keys are
        ignored.

        """
        length = len(self)
        if 0 <= index < length:
            data = self._data
            cuba_works = self._cuba_works
            cubas = self.cubas

            # Find if there are any new CUBA keys to create arrays for.
            new_cubas = (set(value.keys()) & cuba_works.supported) - cubas
            new_arrays = []
            for cuba in new_cubas:
                array = self._cuba_works.empty_array(cuba, length)
                masked = MASKED.format(cuba.name)
                mask = numpy.zeros(shape=array.shape[0], dtype=numpy.uint8)
                new_arrays.append((cuba.name, array))
                new_arrays.append((masked, mask))
            self._add_arrays(new_arrays)

            # Update the attribute values based on ``value``.
            n = data.number_of_arrays
            for array_id in range(n):
                array = data.get_array(array_id)
                array[index] = self._array_value(array.name, value)
        else:
            raise IndexError('{} is out of index range'.format(index))

    def __getitem__(self, index):
        """ Reconstruct a DataContainer from attribute arrays at row=``index``.

        """
        data = self._data
        n = data.number_of_arrays
        arrays = [
            data.get_array(array_id) for array_id in range(0, n, 2)]
        masks = [
            data.get_array(array_id) for array_id in range(1, n, 2)]
        values = {
            CUBA[array.name]: array[index]
            for mask, array in zip(masks, arrays) if mask[index]}
        return DataContainer(values)

    def __delitem__(self, index):
        """ Remove the values from the attribute arrays at row=``index``.

        """
        data = self._data
        n = data.number_of_arrays
        for array_id in range(n):
            data.get_array(array_id).remove_tuple(index)

    def insert(self, index, value):
        """ Insert the values of the DataContainer in the arrays at row=``index``.

        If the provided DataContainer contains new, but supported, cuba keys
        then a new empty array is created for them and updated with
        the associated values of ``value``. Unsupported CUBA keys are
        ignored.

        .. note::

            The underline data structure is better suited for append
            operations. Inserting values in the middle or at the front
            will be less efficient.

        """
        data = self._data
        cubas = self.cubas
        cuba_works = self._cuba_works

        new_cubas = (set(value.keys()) & cuba_works.supported) - cubas
        length = len(self)

        if 0 <= index < length:
            n = data.number_of_arrays
            arrays = []

            # Insert new values in already stored arrays
            for _ in range(n):
                temp = data.get_array(0)
                name = temp.name
                new_value = self._array_value(name, value)
                temp = numpy.insert(temp.to_array(), index, new_value, axis=0)
                arrays.append((name, temp))
                data.remove_array(name)  # remove array from vtk container.

            # Create data and mask arrays from new CUBA keys
            for cuba in new_cubas:
                array = self._cuba_works.empty_array(cuba, length)
                array = numpy.insert(
                    array, index, self._array_value(cuba.name, value), axis=0)
                masked = MASKED.format(cuba.name)
                mask = numpy.zeros(shape=array.shape[0], dtype=numpy.uint8)
                mask[index] = self._array_value(masked, value)
                arrays.append((cuba.name, array))
                arrays.append((masked, mask))

            # Update the vtk container with the extended arrays.
            self._add_arrays(arrays)

        elif index >= length:

            # Add data arrays for new CUBA keys.
            new_arrays = []
            for cuba in new_cubas:
                array = self._cuba_works.empty_array(cuba, length)
                masked = MASKED.format(cuba.name)
                mask = numpy.zeros(shape=array.shape[0], dtype=numpy.uint8)
                new_arrays.append((cuba.name, array))
                new_arrays.append((masked, mask))
            self._add_arrays(new_arrays)

            # Append new values.
            n = data.number_of_arrays
            for array_id in range(n):
                array = data.get_array(array_id)
                array.append(self._array_value(array.name, value))

        else:
            raise IndexError('{} is out of index range'.format(index))

    @classmethod
    def empty(cls, type_=AttributeSetType.POINTS):
        """ Return an empty sequence based wrapping an vtkAttributeDataSet.

        """
        if type_ == AttributeSetType.CELLS:
            return cls(attribute_data=tvtk.CellData())
        else:
            return cls(attribute_data=tvtk.PointData())

    # Private methods ######################################################

    def _add_arrays(self, arrays):
        data = self._data
        for name, array in arrays:
            array_id = data.add_array(array)
            data.get_array(array_id).name = name

    def _array_value(self, name, values):
        try:
            cuba = CUBA[name]
        except KeyError:
            # The array is a mask array.
            return numpy.uint8(CUBA[name.split('-')[0]] in values)
        else:
            # The array is a CUBA attribute array.
            return values.get(cuba, self._cuba_works.defaults[cuba])
