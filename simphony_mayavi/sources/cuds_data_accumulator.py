import warnings

import numpy

from simphony.testing.utils import dummy_cuba_value


class CUDSDataAccumulator(object):
    """ Accumulate data information per CUBA key.

    """
    def __init__(self, keys=()):
        self._keys = set(keys)
        self._expand_mode = len(keys) == 0
        self._data = {}
        self._record_size = 0
        self._default_values = {}
        self._expand(self._keys)

    @property
    def keys(self):
        return set(self._keys)

    def append(self, data):
        if self._expand_mode:
            new_keys = set(data.keys()) - self._keys
            self._keys.update(new_keys)
            self._expand(new_keys)
        for key in self._keys:
            self._data[key].append(data.get(key, None))
        self._record_size += 1

    def _expand(self, keys):
        for key in keys:
            self._default_values[key] = _cuba_default(key)
            self._data[key] = [None] * self._record_size

    def __len__(self):
        return self._record_size

    def __getitem__(self, key):
        return self._data[key]

    def load_onto_vtk(self, vtk_data):
        for cuba in self.keys:
            default = self._default_values[cuba]
            if isinstance(default, (float, int)):
                data = numpy.array(self._data[cuba], dtype=float)
                index = vtk_data.add_array(data)
                vtk_data.get_array(index).name = cuba.name
            else:
                message = 'proprrty {!r} is currently ignored'
                warnings.warn(message.format(cuba))


def _cuba_default(cuba):
    value = dummy_cuba_value(cuba)
    if isinstance(value, (float, int)):
        return numpy.NaN
    else:
        return None
