from traits.api import (
    HasStrictTraits, Callable, Either, List, Dict, Instance)


class CUDSDataExtractor(HasStrictTraits):
    """  Extract data from cuds items.
    """

    #: The function to call that iterates over the desired items. Iteration 
    #: should return a tuple of (uid, data).
    function = Callable

    # The list of keys to restrict the data extraction.
    keys = Either(None, List(UUID))

    #: The list of cuba keys that are available (read only)
    available = Property(List(CUBA), depends_on='function')

    #: Currently selected CUBA key
    selected = Instance(CUBA)

    #: The dictionary mapping uid to the extracted value.
    data = Property(Dict(Instance(UUID), Any), depends_on='selected, available')
