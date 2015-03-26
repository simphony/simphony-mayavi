import warnings

import numpy

from simphony.testing.utils import dummy_cuba_value


class CUDSDataAccumulator(object):
    """ Accumulate data information per CUBA key.

    A collector object that stores the information of the added
    :class:`~DataContainer` into a list of values per CUBA key.
    The currently stored values can be retrieved based by CUBA key.

    Example::

      >>> accumulator = CUDSDataAccumulator():
      >>> accumulator.append(DataContainer(TEMPERATURE=34))
      >>> accumulator.append(DataContainer()
      >>> accumulator.append(DataContainer(TEMPERATURE=56))
      >>> accumulator.keys()
      {CUBA.TEMPERATURE}
      >>> accumulator[CUBA.TEMPERATURE]
      [34, None, 56]


    """
    def __init__(self, keys=()):
        """ Constructor

        Parameters
        ----------
        keys : list

            The list of keys that the accumulator should care
            about. Providing this value at initialisation sets up the
            accumulator to ``fixed`` mode where only the provided keys
            will be stored. IF no keys are provided then all keys with
            value will be stored and the accumulator operates in
            ``expand`` mode where every newly seen key will be added
            to the set of keys and initialised with missing values.

        """
        self._keys = set(keys)
        self._expand_mode = len(keys) == 0
        self._data = {}
        self._record_size = 0
        self._expand(self._keys)

    @property
    def keys(self):
        """ The set of CUBA keys that this accumulator contains.

        """
        return set(self._keys)

    def append(self, data):
        """ Append info from a ``DataContainer``.

        Parameters
        ----------
        data : DataContainer
            The data information to append.

        If the accumulator operates in ``fixed`` mode:

        - Any keys in self.keys() that have values in ``data`` will be stored
          (appended to the related key lits).
        - Missing keys will be store as ``None``
        - New keys will be ignored

        If the accumulator operates in ``expand`` mode:

        - Any new keys in `Data` will be added to the :code:`self.keys()` list
          and the related list of values with length equal to the current
          record size will be initialised with values of ``None``.
        - Any keys in the modified :code:`self.keys()` that have values in
          ``data`` will be stored (appended to the related key lits).
        - Missing keys will be store as ``None``.

        """
        if self._expand_mode:
            new_keys = set(data.keys()) - self._keys
            self._keys.update(new_keys)
            self._expand(new_keys)
        for key in self._keys:
            self._data[key].append(data.get(key, None))
        self._record_size += 1

    def load_onto_vtk(self, vtk_data):
        """ Load the stored information onto a vtk data container.

        Parameters
        ----------
        vtk_data : vtkPointData or vtkCellData
            The vtk container to load the value onto.

        Data are loaded onto the vtk container based on their data
        type. The name of the added array is the name of the CUBA key
        (i.e. :samp:`{CUBA}.name`). Currently only scalars and there
        dimensional vectors are supported.

        """
        for cuba in self.keys:
            default = dummy_cuba_value(cuba)
            if isinstance(default, (float, int)):
                data = numpy.array(self._data[cuba], dtype=float)
                index = vtk_data.add_array(data)
                vtk_data.get_array(index).name = cuba.name
            elif isinstance(default, numpy.ndarray) and len(default) == 3:
                nan = numpy.array([None, None, None], dtype=float)
                replacer = lambda x: nan if x is None else x
                data = numpy.array(
                    tuple(replacer(data) for data in self._data[cuba]),
                    dtype=numpy.float)
                index = vtk_data.add_array(data)
                vtk_data.get_array(index).name = cuba.name
            else:
                message = 'property {!r} is currently ignored'
                warnings.warn(message.format(cuba))

    def __len__(self):
        """ The number of values that are stored per key

        .. note:: Behaviour it temporary and will probably change soon.

        """
        return self._record_size

    def __getitem__(self, key):
        """ Get the list of accumulated values for the CUBA key.

        Parameters
        ----------
        key : CUBA
            A CUBA Enum value

        Returns
        -------
        result : list
            A list of data values collected for ``key``. Missing values
            are designated with ``None``.

        """
        return self._data[key]

    def _expand(self, keys):
        for key in keys:
            self._data[key] = [None] * self._record_size
