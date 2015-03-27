import warnings

import numpy

from simphony.testing.utils import dummy_cuba_value


class CUDSDataAccumulator(object):
    """ Accumulate data information per CUBA key.

    A collector object that stores :class:``DataContainer`` data into
    a list of values per CUBA key. By appending :class:`DataContainer`
    instanced the user can effectively convert the per item mapping of
    data values in a CUDS container to a per CUBA key mapping of the
    data values (useful for coping data to vtk array containers).

    The Accumulator has two modes of operation ``fixed`` and
    ``expand``. ``fixed`` means that data will be stored for
    a predefined set of keys on every ``append`` call and missing
    values will be saved as ``None``. Where ``expand`` will extend
    the internal table of values when ever a new key is introduced.

    .. rubric:: expand operation

    >>> accumulator = CUDSDataAccumulator():
    >>> accumulator.append(DataContainer(TEMPERATURE=34))
    >>> accumulator.keys()
    {CUBA.TEMPERATURE}
    >>> accumulator.append(DataContainer(VELOCITY=(0.1, 0.1, 0.1))
    >>> accumulator.append(DataContainer(TEMPERATURE=56))
    >>> accumulator.keys()
    {CUBA.TEMPERATURE, CUBA.VELOCITY}
    >>> accumulator[CUBA.TEMPERATURE]
    [34, None, 56]
    >>> accumulator[CUBA.VELOCITY]
    [None, (0.1, 0.1, 0.1), None]

    .. rubric:: fixed operation

    >>> accumulator = CUDSDataAccumulator([CUBA.TEMPERATURE, CUBA.PRESSURE]):
    >>> accumulator.keys()
    {CUBA.TEMPERATURE, CUBA.PRESSURE}
    >>> accumulator.append(DataContainer(TEMPERATURE=34))
    >>> accumulator.append(DataContainer(VELOCITY=(0.1, 0.1, 0.1))
    >>> accumulator.append(DataContainer(TEMPERATURE=56))
    >>> accumulator.keys()
    {CUBA.TEMPERATURE, CUBA.PRESSURE}
    >>> accumulator[CUBA.TEMPERATURE]
    [34, None, 56]
    >>> accumulator[CUBA.PRESSURE]
    [None, None, None]
    >>> accumulator[CUBA.VELOCITY]
    KeyError(...)

    """
    def __init__(self, keys=()):
        """Constructor

        Parameters
        ----------
        keys : list

            The list of keys that the accumulator should care
            about. Providing this value at initialisation sets up the
            accumulator to operate in ``fixed`` mode. If no keys are
            provided then accumulator operates in ``expand`` mode.

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

        - Any keys in :code:`self.keys()` that have values in ``data``
          will be stored (appended to the related key lits).
        - Missing keys will be stored as ``None``

        If the accumulator operates in ``expand`` mode:

        - Any new keys in `Data` will be added to the :code:`self.keys()` list
          and the related list of values with length equal to the current
          record size will be initialised with values of ``None``.
        - Any keys in the modified :code:`self.keys()` that have values in
          ``data`` will be stored (appended to the list of the related key).
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
        (i.e. :samp:`{CUBA}.name`). Currently only scalars and three
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

        .. note:: Behaviour is temporary and will probably change soon.

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
