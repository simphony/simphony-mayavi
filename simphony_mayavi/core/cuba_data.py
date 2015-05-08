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


class CubaData(MutableSequence):
    """Map a vtkCellData or vtkPointData object to a sequence of DataContainers.

    The class implements the :class:`MutableSequence` api to wrap a
    :class:`tvtk.CellData` or :class:`tvtk.PointData` array where each
    CUBA key is a :class:`tvtk.DataArray`. The aim is to help the
    conversion between column based structure of the
    :class:`vtkCellData` or :class:`vtkPointData` and the row based
    access provided by a list of
    :class:`~.DataContainer<DataContainers>`.


    """

    def __init__(self, attribute_data, cuba_works=None):
        self._data = attribute_data
        if cuba_works is None:
            cuba_works = CUBAWorks.default()
        self._cuba_works = cuba_works

    @property
    def cubas(self):
        """ The set of currently stored cuba keys.

        For each cuba key there is an associated :class:`vtk.DataArray`.

        """
        data = self._data
        n = data.number_of_arrays
        return {CUBA[data.get_array(index).name] for index in range(n)}

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

        If the provided value contains new, but supported, cuba keys
        then a new empty array is created for them and updated with
        the associated values of ``value``.  Unsupported CUBA keys are
        ignored.

        """
        length = len(self)
        if 0 <= index < length:
            data = self._data
            cuba_works = self._cuba_works
            cubas = self.cubas
            new_cubas = (set(value.keys()) & cuba_works.supported) - cubas
            arrays = (
                (cuba, cuba_works.empty_array(cuba, length))
                for cuba in new_cubas)
            self._add_arrays(arrays)
            n = data.number_of_arrays
            defaults = cuba_works.defaults
            for array_id in range(n):
                array = data.get_array(array_id)
                cuba = CUBA[array.name]
                array[index] = value.get(cuba, defaults[cuba])
        else:
            raise IndexError('{} is out of index range'.format(index))

    def __getitem__(self, index):
        """ Reconstruct a DataContainer from array values at row=``index``.

        """
        data = self._data
        n = data.number_of_arrays
        arrays = [data.get_array(array_id) for array_id in range(n)]
        defaults = self._cuba_works.defaults
        values = {}
        for array in arrays:
            value = array[index]
            cuba = CUBA[array.name]
            default = defaults[cuba]
            # FIXME: implement a masked based logic
            if numpy.isscalar(default):
                if not numpy.isclose(value, default, 0.0, 0.0, True):
                    values[cuba] = value
            else:
                if not all(numpy.isclose(value, default, 0.0, 0.0, True)):
                    values[cuba] = value
        return DataContainer(values)

    def __delitem__(self, index):
        """ Remove the values from the arrays at row=``index``.

        """
        data = self._data
        n = data.number_of_arrays
        for array_id in range(n):
            data.get_array(array_id).remove_tuple(index)

    def insert(self, index, value):
        """ Insert the values of the DataContainer in the arrays at row=``index``.

        If the provided DataContainer contains new, but supported, cuba keys
        then a new empty array is created for them and updated with
        the associated values of ``value``.  Unsupported CUBA keys are
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
        defaults = cuba_works.defaults
        length = len(self)
        if 0 <= index < length:
            n = data.number_of_arrays
            arrays = []
            for _ in range(n):
                temp = data.get_array(0)
                cuba = CUBA[temp.name]
                temp = numpy.insert(
                    temp.to_array(), index,
                    value.get(cuba, defaults[cuba]), axis=0)
                data.remove_array(cuba.name)
                arrays.append((cuba, temp))
            for cuba in new_cubas:
                array = self._cuba_works.empty_array(cuba, length)
                array = numpy.insert(
                    array, index, value.get(cuba, defaults[cuba]), axis=0)
                arrays.append((cuba, array))
            self._add_arrays(arrays)
        elif index >= length:
            new_arrays = (
                (cuba, self._cuba_works.empty_array(cuba, length))
                for cuba in new_cubas)
            self._add_arrays(new_arrays)
            n = data.number_of_arrays
            for array_id in range(n):
                array = data.get_array(array_id)
                cuba = CUBA[array.name]
                array.append(value.get(cuba, defaults[cuba]))
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
        for cuba, array in arrays:
            array_id = data.add_array(array)
            data.get_array(array_id).name = cuba.name
