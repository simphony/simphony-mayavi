import numpy
import warnings

from simphony.core.keywords import KEYWORDS
from simphony.core.cuba import CUBA


def supported_cuba():
    """ Return the list of CUBA keys that can be supported by vtk.


    """
    return {
        cuba for cuba in CUBA
        if default_cuba_value(cuba) is not None}


def default_cuba_value(cuba):
    """ Return the default value of the CUBA key as a scalar or numpy array.

    Int type values have ``-1`` as default, while float type values
    have ``numpy.nan``.

    .. note::

       Only vector and scalar values are currently supported.

    """
    description = KEYWORDS[cuba.name]

    if description.dtype is None:
        return None

    if description.shape == [1]:
        if numpy.issubdtype(description.dtype, numpy.float):
            return numpy.nan
        elif numpy.issubdtype(description.dtype, numpy.int):
            return -1
        else:
            message = 'ignored property {!r} : not a float or int'
            warnings.warn(message.format(cuba))
    elif description.shape == [3]:
        if numpy.issubdtype(description.dtype, numpy.float):
            return numpy.array(
                [numpy.nan, numpy.nan, numpy.nan], dtype=description.dtype)
        elif numpy.issubdtype(description.dtype, numpy.int):
            return numpy.array([-1, -1, -1], dtype=description.dtype)
        else:
            message = 'ignored property {!r} : not a float or int'
            warnings.warn(message.format(cuba))
    else:
        message = 'ignored property {!r} : not a vector or scalar'
        warnings.warn(message.format(cuba))


def empty_array(cuba, length, fill=None):
    """ Return an array filled with the default value for CUBA.

    Parameters
    ----------
    cuba : CUBA
        The CUBA key to use to base the array data.
    length : tuple
        The length of the array in CUBA value items.
    fill :
        The scalar or array value to fill for every CUBA item.

    Returns
    -------
    data : ndarray

    """
    description = KEYWORDS[cuba.name]
    shape = [length] + description.shape
    data = numpy.empty(shape=shape, dtype=description.dtype)
    default = default_cuba_value(cuba) if fill is None else fill

    if shape[1] == 1:
        data.fill(default)
    else:
        for index, value in enumerate(default):
            data[:, index] = value
    return data
