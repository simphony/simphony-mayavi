from collections import MutableSequence

import numpy
from tvtk.api import tvtk
from tvtk.array_handler import _array_cache
from enum import Enum
from simphony.core.cuba import CUBA
from simphony.core.keywords import KEYWORDS
from simphony.core.data_container import DataContainer

from simphony_mayavi.core.cuba_utils import (
    supported_cuba, default_cuba_value, empty_array)


class AttributeSetType(Enum):
    """ Enum to the supported DatasetAttribute types.

    """
    POINTS = 1
    CELLS = 2


class CubaData(MutableSequence):
    """ Map a vtkCellData or vtkPointData object to a sequence of DataContainers.

    The class implements the :class:`MutableSequence` api to wrap a
    :class:`tvtk.CellData` or :class:`tvtk.PointData` array where each
    CUBA key is a :class:`tvtk.DataArray`. The aim is to help the
    conversion between column based structure of the
    :class:`vtkCellData` or :class:`vtkPointData` and the row based
    access provided by a list of
    :class:`~.DataContainer<DataContainers>`.

    While the wrapped tvtk container is empty the following behaviour is
    active:

    - Using ``len`` will return the ``initial_size``, if defined, or 0.
    - Using element access will return an empty `class:~.DataContainer`.
    - No field arrays have been allocated.

    When values are first added/updated with non-empty ``DataContainers``
    then the necessary arrays are created and the ``initial_size`` info
    is not used anymore.

    .. note::

       Missing values for the attribute arrays are stored in separate
       attribute arrays named "<CUBA.name>-mask" as ``0`` while
       present values are designated with a ``1``.

    """
    def __init__(
            self, attribute_data, stored_cuba=None, size=None, masks=None):
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

        mask : tvtk.FieldData
            A data arrays containing the mask of some of the CUBA data in
            ``attribute_data``.

        Raises
        ------
        ValueError :
            When a non-empty ``attribute_data`` container is provided while
            size != None.

        """
        check_attribute_arrays(attribute_data)
        check_masks(masks)

        if attribute_data.number_of_arrays != 0 and size is not None:
            message = "Using initial_size for a non-empty dataset is invalid"
            raise ValueError(message)

        self._data = attribute_data
        if stored_cuba is None:
            stored_cuba = supported_cuba()
        self._stored_cuba = stored_cuba
        self.masks = self._initialize_masks(masks)
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
        return {CUBA[name] for name in self._names}

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
            masks = self.masks
            stored = self._stored_cuba
            cubas = self.cubas

            # Find if there are any new CUBA keys to create arrays for.
            new_cubas = (set(value.keys()) & stored) - cubas
            self._add_new_arrays(new_cubas, length)

            # Update the attribute values based on ``value``.
            n = data.number_of_arrays
            for array_id in range(n):
                array = data.get_array(array_id)
                mask = masks.get_array(array_id)
                cuba = CUBA[array.name]
                value_to_set = value.get(cuba, self._defaults[cuba])
                array[index] = (value_to_set
                                if value_to_set is not None else 0.0)
                mask[index] = (cuba in value, value_to_set is None)
        else:
            raise IndexError('{} is out of index range'.format(index))

    def __getitem__(self, index):
        """ Reconstruct a DataContainer from attribute arrays at row=``index``.

        """
        if abs(index) > len(self):
            raise IndexError('{} is out of index range'.format(index))
        data = self._data
        names = self._names
        arrays = [data.get_array(name) for name in names]
        masks = [self.masks.get_array(name) for name in names]
        values = {
            CUBA[array.name]: (
                KEYWORDS[array.name].dtype(array[index])
                if mask[index][1] == 0.0
                else None
            )
            for mask, array in zip(masks, arrays) if mask[index][0] == 1.0}
        return DataContainer(values)

    def __delitem__(self, index):
        """ Remove the values from the attribute arrays at row=``index``.

        """
        length = len(self)
        if abs(index) > length:
            raise IndexError('{} is out of index range'.format(index))
        data = self._data
        masks = self.masks
        n = data.number_of_arrays
        if n == 0 and len(self) != 0:
            self._virtual_size -= 1
        else:
            if len(self) != 1:
                for array_id in range(n):
                    data.get_array(array_id).remove_tuple(index)
                    # bit arrays do not support the remove tuple operation
                    # properly.
                    bit_array = masks.get_array(array_id)
                    if index == length:
                        bit_array.remove_last_tuple(index)
                    else:
                        temp = bit_array.to_array()
                        bit_array.from_array(numpy.delete(temp, index, axis=0))
            else:
                for array_id in reversed(range(n)):
                    name = data.get_array_name(array_id)
                    data.remove_array(name)
                    masks.remove_array(name)

    def insert(self, index, value):
        """ Insert the values of the DataContainer in the arrays at
        row=``index``.

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
        masks = self.masks
        cubas = self.cubas
        stored_cuba = self._stored_cuba

        new_cubas = (set(value.keys()) & stored_cuba) - cubas
        length = len(self)
        if 0 <= index < length:
            n = data.number_of_arrays
            arrays = []
            mask_arrays = []

            # Insert new values in already stored arrays
            for _ in range(n):
                temp = data.get_array(0)
                name = temp.name
                cuba = CUBA[name]
                new_value = value.get(cuba, self._defaults[cuba])
                temp = numpy.insert(temp.to_array(),
                                    index,
                                    (new_value
                                     if new_value is not None else 0.0
                                     ),
                                    axis=0)
                arrays.append((name, temp))
                data.remove_array(name)  # remove array from vtk container.
                temp = masks.get_array(0)
                temp = numpy.insert(temp.to_array(),
                                    index,
                                    (cuba in value, new_value is None),
                                    axis=0)
                mask_arrays.append((name, temp))
                masks.remove_array(name)  # remove array from vtk container.

            # Create data and mask arrays from new CUBA keys
            for cuba in new_cubas:
                array = empty_array(cuba, length + 1)
                mask = numpy.zeros(shape=(length + 1, 2), dtype=numpy.int8)
                value_to_set = value.get(cuba, self._defaults[cuba])

                array[index] = (value_to_set
                                if value_to_set is not None else 0.0)
                mask[index, :] = (int(cuba in value),
                                  int(value_to_set is None))
                arrays.append((cuba.name, array))
                mask_arrays.append((cuba.name, mask))

            # Update the vtk container with the extended arrays.
            self._add_arrays(arrays)
            self._add_masks(mask_arrays)

        elif index >= length:

            # Add data arrays for new CUBA keys.
            self._add_new_arrays(new_cubas, length)

            # Append new values.
            n = data.number_of_arrays
            for array_id in range(n):
                array = data.get_array(array_id)
                cuba = CUBA[array.name]
                value_to_set = value.get(cuba, self._defaults[cuba])
                array.append(value_to_set if value_to_set is not None else 0.0)
                # invalidate the numpy cache, see issue
                # https://github.com/enthought/mayavi/issues/197
                _array_cache._remove_array(tvtk.to_vtk(array).__this__)
                array = masks.get_array(array_id)
                array.append((cuba in value, value_to_set is None))
                # invalidate the numpy cache, see issue
                # https://github.com/enthought/mayavi/issues/197
                _array_cache._remove_array(tvtk.to_vtk(array).__this__)
        else:
            raise IndexError('{} is out of index range'.format(index))

        # make sure that virtual_size is properly updated
        n = data.number_of_arrays
        if n == 0:
            # If there are no arrays yet we need to use the virtual
            # size attribute.
            if self._virtual_size is not None:
                self._virtual_size += 1
            else:
                self._virtual_size = 1
        else:
            self._virtual_size = None

    def __str__(self):
        return u"[{}]".format(",".join(str(item) for item in self))

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

    def _add_masks(self, arrays):
        masks = self.masks
        for name, array in arrays:
            bit_array = tvtk.BitArray()
            bit_array.number_of_components = 2
            bit_array.name = name
            bit_array.from_array(array)
            masks.add_array(bit_array)

    def _add_new_arrays(self, cubas, length):
        new_arrays = []
        new_masks = []
        for cuba in cubas:
            array = empty_array(cuba, length)
            mask = numpy.zeros(shape=(length, 2), dtype=numpy.int8)
            new_arrays.append((cuba.name, array))
            new_masks.append((cuba.name, mask))
        self._add_arrays(new_arrays)
        self._add_masks(new_masks)

    def _initialize_masks(self, default=None):
        """ Initialise the masks tvtk.FieldData.

        .. note::

           We assume that all the arrays have the same number of components.

        """
        data = self._data
        masks = tvtk.FieldData()

        if data.number_of_arrays == 0:
            return masks

        length = len(data.get_array(0))
        for array_id in range(data.number_of_arrays):
            name = data.get_array_name(array_id)
            if CUBA[name] not in self._stored_cuba:
                continue
            mask = tvtk.BitArray()
            mask.number_of_components = 2

            if default is not None and default.has_array(name):
                array = default.get_array(name).to_array()
            else:
                # First bit is value 1: present 0: not present.
                # Second bit is 1: None, 0: not None.
                array = numpy.zeros(shape=(length, 2), dtype=numpy.int8)
                array[:, 0] = 1

            mask.from_array(array)
            mask.name = name
            masks.add_array(mask)

        return masks


def check_attribute_arrays(attribute_data):
    """ check the vtk attribute array container.

    The function checks that the container has only CUBA related arrays
    and that they all have the same length.

    """
    data = attribute_data

    # check invalid array names
    names = [
        data.get_array_name(array_id)
        for array_id in range(data.number_of_arrays)]
    try:
        for name in names:
            CUBA[name]
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


def check_masks(masks):
    """Check if the masks in input comply with the expected (n, 2)
    or are None"""
    if masks is None:
        return

    for index in range(masks.number_of_arrays):
        mask = masks.get_array(index)
        if mask.number_of_components != 2:
            raise ValueError("Mask must have two components")
