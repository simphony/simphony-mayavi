import numpy
import warnings

from simphony.core.keywords import KEYWORDS
from simphony.core.cuba import CUBA


def supported_cuba():
    return [
        cuba for cuba in CUBA
        if default_cuba_value(cuba) is not None]


def default_cuba_value(cuba):
    description = KEYWORDS[cuba.name]
    if description.shape == [1]:
        if numpy.issubdtype(description.dtype, numpy.float):
            return numpy.nan
        elif numpy.issubdtype(description.dtype, numpy.int):
            return -1
        else:
            message = 'property {!r} is currently ignored'
            warnings.warn(message.format(cuba))
    elif description.shape == [3]:
        if numpy.issubdtype(description.dtype, numpy.float):
            return numpy.array(
                [numpy.nan, numpy.nan, numpy.nan], dtype=description.dtype)
        elif numpy.issubdtype(description.dtype, numpy.int):
            return numpy.array([-1, -1, -1], dtype=description.dtype)
        else:
            message = 'property {!r} is currently ignored'
            warnings.warn(message.format(cuba))
    else:
        message = 'property {!r} is currently ignored'
        warnings.warn(message.format(cuba))


class CUBAWorks(object):
    """ A utility instance to manage CUBA to vtk_arrays conversions.

    """
    def __init__(self, supported, defaults):
        """ Constructor

        """
        self.supported = supported
        self.defaults = defaults

    def empty_array(self, cuba, size):
        """ Return an array filled with the default value for CUBA.
        """
        if cuba in self.supported:
            description = KEYWORDS[cuba.name]
            shape = [size] + description.shape
            data = numpy.empty(shape=shape, dtype=description.dtype)
            default = self.defaults[cuba]
            if shape[1] == 1:
                data.fill(default)
            elif len(set(default)) == 1:
                data.fill(default)
            else:
                for index, value in enumerate(default):
                    data[:, index] = value
            return data
        else:
            raise ValueError('{} is not supported'.format(cuba))

    @classmethod
    def default(cls):
        supported = supported_cuba()
        defaults = {cuba: default_cuba_value(cuba) for cuba in supported}
        return cls(supported, defaults)

    @classmethod
    def custom(cls, supported=None, defaults=None):
        supported = supported_cuba() if supported is None else supported
        if defaults is None:
            defaults = {cuba: default_cuba_value(cuba) for cuba in supported}
        else:
            defaults = {cuba: defaults[cuba] for cuba in supported}
        return cls(supported, defaults)
