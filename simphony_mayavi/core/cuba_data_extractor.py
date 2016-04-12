import uuid

from simphony.core.cuba import CUBA

from traits.api import (
    HasStrictTraits, ReadOnly, Either, Set, Dict,
    Instance, Property, Any, cached_property, on_trait_change)

CUBATrait = Instance(CUBA)
UUID = Instance(uuid.UUID)


class CUBADataExtractor(HasStrictTraits):
    """Extract cuba data from cuds items iterable.

    The class that supports extracting data values of a specific CUBA key
    from an iterable that returns low level CUDS objects
    (e.g. :class:`~Point`).

    """

    #: The function to call that returns a generator over the desired
    #: items (e.g. Mesh.iter_points). This value cannot be changed after
    #: initialisation.
    function = ReadOnly

    #: The list of uuid keys to restrict the data extraction. This attribute
    #: is passed to the function generator method to restrict iteration over
    #: the provided keys (e.g Mesh.iter_points(uids=keys))
    keys = Either(None, Set(UUID))

    #: The list of cuba keys that are available (read only). The value is
    #: recalculated at initialialisation and when the ``reset`` method is
    #: called.
    available = Property(Set(CUBATrait), depends_on='_available')

    #: Currently selected CUBA key. Changing the selected key will fire events
    #: that will result in executing the generator function and extracting
    #: the related values from the CUDS items that the iterator yields. The
    #: resulting mapping of ``uid -> value`` will be stored in ``data``.
    selected = CUBATrait

    #: The dictionary mapping of item uid to the extracted data value. A change
    #: Event is fired for ``data`` when ``selected`` or ``keys`` change or
    #: the ``reset`` method is called.
    data = Property(Dict(UUID, Any), depends_on='_data')

    # Private traits #########################################################

    _available = Set(CUBATrait)

    _data = Dict(UUID, Any)

    # Constructor ############################################################

    def __init__(self, **traits):
        super(CUBADataExtractor, self).__init__(**traits)
        # Reset the data information after all necessary value have been set.
        self.reset()

    # Property getters setters ###############################################

    @cached_property
    def _get_available(self):
        return self._available

    @cached_property
    def _get_data(self):
        return self._data

    # Public methods  ########################################################

    def reset(self):
        """ Reset the ``available`` and ``data`` attributes.

        """
        function = self.function
        generator = function(self.keys)
        available = set()
        selected = self.selected
        if selected is None:
            for item in generator:
                available.update(item.data.keys())
        else:
            data = {}
            for item in generator:
                data[item.uid] = item.data.get(selected, None)
                available.update(item.data.keys())
            self._data = data
        self._available = available

    # Change handlers ########################################################

    @on_trait_change('selected,keys', post_init=True)
    def _selected_updated(self):
        selected = self.selected
        generator = self.function(self.keys)
        if selected is None:
            self._data = {}
        else:
            self._data = {
                item.uid: item.data.get(selected, None)
                for item in generator}
