from collections import MutableSequence

import numpy
from tvtk.api import tvtk
from enum import Enum
from simphony.core.cuba import CUBA
from simphony.core.data_container import DataContainer

from simphony_mayavi.core.cuba_utils import (
    supported_cuba, default_cuba_value, empty_array)


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

    def __init__(self, attribute_data, stored_cuba=None):
        """ Constructor

        Parameters
        ----------
        attribute_data: tvtk.DataSetAttributes
            The vtk attribute container.
        stored_cuba : set
            The CUBA keys that are going to be stored default
            is the result of running :meth:`supported_cuba`

        """
        self._fix_arrays(attribute_data)
        self._data = attribute_data
        if stored_cuba is None:
            stored_cuba = supported_cuba()
        self._stored_cuba = stored_cuba
        self._defaults = {
            cuba: default_cuba_value(cuba)
            for cuba in stored_cuba}

    @property
    def cubas(self):
        """ The set of currently stored CUBA keys.

        For each cuba key there is an associated
        :class:`~.DataArray` connected to the :class:`~.PointData`
        or :class:`~.CellData`

        """
        return {CUBA[name] for name in self._names if '-mask' not in name}

    @property
    def _names(self):
        data = self._data
        return {
            data.get_array_name(array_id): array_id
            for array_id in range(data.number_of_arrays)}

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
            stored = self._stored_cuba
            cubas = self.cubas

            # Find if there are any new CUBA keys to create arrays for.
            new_cubas = (set(value.keys()) & stored) - cubas
            new_arrays = []
            for cuba in new_cubas:
                array = empty_array(cuba, length)
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
        names = self._names
        arrays = [
            data.get_array(names[name])
            for name in names if '-mask' not in name]
        masks = [
            data.get_array(names[name])
            for name in names if '-mask' in name]
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
        stored_cuba = self._stored_cuba

        new_cubas = (set(value.keys()) & stored_cuba) - cubas
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
                array = empty_array(cuba, length)
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
                array = empty_array(cuba, length)
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
            return values.get(cuba, self._defaults[cuba])

    def _fix_arrays(self, attribute_data):
        data = attribute_data

        # check invalid array names
        names = [
            data.get_array_name(array_id)
            for array_id in range(data.number_of_arrays)]
        try:
            cubas = [CUBA[name] for name in names if '-mask' not in name]
        except KeyError:
            raise ValueError("vtk object contains non cuba named arrays")

        # check array length
        lengths = {
            len(data.get_array(array_id))
            for array_id in range(data.number_of_arrays)}
        if len(lengths) > 1:
            info = {
                data.get_array_name(array_id): len(
                    data.get_array_name(array_id))
                for array_id in range(data.number_of_arrays)}
            message = "vtk object arrays are not the same size: {}"
            raise ValueError(message.format(info))
        elif len(lengths) == 0:
            # empty vtk object
            return
        else:
            # fix masked arrays
            length = next(iter(lengths))
            masks = [name for name in names if '-mask' in name]
            for cuba in cubas:
                masked = MASKED.format(cuba.name)
                if masked not in masks:
                    mask = numpy.ones(shape=length, dtype=numpy.uint8)
                    array_id = data.add_array(mask)
                    data.get_array(array_id).name = masked
