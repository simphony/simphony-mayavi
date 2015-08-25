from mayavi.core.api import registry

from simphony_mayavi.adapt2cuds import adapt2cuds


def load(filename, name=None, kind=None, rename_arrays=None):
    """ Load the file data into a CUDS container.

    Parameters
    ----------
    filename : string
        The file name of the file to load.

    name : string
        The name of the returned CUDS container. Default is 'CUDS container'.

    kind :
        The kind {'mesh', 'lattice', 'particles'} of the container to return.
        Default is None, where the function will use some heuristics to
        infer the most appropriate type of CUDS container to return
        (using adapt2cuds).

    rename_array : dict
        Dictionary mapping the array names used in the dataset object
        to their related CUBA keywords that will be used in the returned
        CUDS container.

        .. note::

           Only CUBA keywords are supported for array names so use this
           option to provide a translation mapping to the CUBA keys.

    """
    data_set = _read(filename)
    return adapt2cuds(
        data_set, name, kind, rename_arrays)


def _read(filename):
    """ Find a suitable reader and read the tvtk.Dataset.
    """
    metasource = registry.get_file_reader(filename)
    if metasource is None:
        message = 'No suitable reader found for file: {}'
        raise RuntimeError(message.format(filename))
    if metasource.factory is None:
        source = metasource.get_callable()()
        source.initialize(filename)
        source.update()
        reader = source.reader
    else:
        message = 'Mayavi reader that requires a scene is not supported : {}'
        raise NotImplementedError(message.format(filename))

    if len(source.outputs) != 1:
        message = 'Only one output is expected from the reader'
        raise RuntimeError(message)
    return reader.output
