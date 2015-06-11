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

    While the wrapped tvkt container is empty the following behaviour is
    active:

    - Using ``len`` will return the ``initial_size``, if defined, or 0.
    - Using element access will return an empty `class:~.DataContainer`.
    - No field arrays have been allocated.

    When values are first added/updated with non-empty ``DataContainers``
    then the necessary arrays are created and the ``initial_size`` info
    is not used anymore.

    .. note::

       - Missing values for the attribute arrays are stored in separate
         attribute arrays named "<CUBA.name>-mask" as ``0`` while
         present values are designated with a ``1``.

    """

    def __init__(self, attribute_data, stored_cuba=None, size=None):
        """ Constructor

        Parameters
        ----------
        attribute_data: tvtk.DataSetAttributes
            The vtk attribute container.
        stored_cuba : set
            The CUBA keys that are going to be stored default
            is the result of running :meth:`supported_cuba`
        size : int
            The initial size of the container. Default is None. Setting
            a value will activate the virtual size behaviour of the container.

        Raises
        ------
        ValueError :
            When a non-empty ``attribute_data`` container is provided while
            size != None.

        """
        fix_attribute_arrays(attribute_data)

        if attribute_data.number_of_arrays != 0 and size is not None:
            message = "Using initial_size for a non-empty dataset is invalid"
            raise ValueError(message)

        self._data = attribute_data
        if stored_cuba is None:
            stored_cuba = supported_cuba()
        self._stored_cuba = stored_cuba
        self._defaults = {
            cuba: default_cuba_value(cuba)
            for cuba in stored_cuba}
        self._virtual_size = size

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
        virtual_size = self._virtual_size
        length = 0 if virtual_size is None else virtual_size
        data = self._data
        if data.number_of_arrays == 0:
            return length
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
        if abs(index) > len(self):
            raise IndexError('{} is out of index range'.format(index))
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
        if n == 0 and len(self) != 0:
            self._virtual_size -= 1

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
            else:
                # If there are no arrays yet we need to use the virtual
                # size attribute.
                if self._virtual_size is not None:
                    self._virtual_size += 1
                else:
                    self._virtual_size = 1

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
                # If there are no arrays yet we need to use the virtual
                # size attribute.
                if self._virtual_size is not None:
                    self._virtual_size += 1
                else:
                    self._virtual_size = 1
        else:
            raise IndexError('{} is out of index range'.format(index))

    @classmethod
    def empty(cls, type_=AttributeSetType.POINTS, size=0):
        """ Return an empty sequence based wrapping a vtkAttributeDataSet.

        Parameters
        ----------
        size : int
            The virtual size of the container.

        type_ : AttributeSetType
            The type of the vtkAttributeSet to create.

        """
        if type_ == AttributeSetType.CELLS:
            return cls(attribute_data=tvtk.CellData(), size=size)
        else:
            return cls(attribute_data=tvtk.PointData(), size=size)

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


def fix_attribute_arrays(attribute_data):
    """ Fix the layout of the vtk attribute array container.

    The function check that the container has only CUBA related arrays
    and that they all have the same length. Any masks that are missing
    are added to the container.

    """
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
