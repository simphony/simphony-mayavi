import uuid

from simphony.core.cuba import CUBA

from traits.api import (
    HasStrictTraits, ReadOnly, Either, Set, Dict,
    Instance, Property, Any, cached_property, on_trait_change)

CUBATrait = Instance(CUBA)
UUID = Instance(uuid.UUID)


class CUDSDataExtractor(HasStrictTraits):
    """  Extract data from cuds items.
    """

    #: The function to call that returns a generator over the desired
    #: items. Iteration should return a tuple of (uid, data). This
    #: value cannot be changed after initialisation.
    function = ReadOnly

    # The list of keys to restrict the data extraction.
    keys = Either(None, Set(UUID))

    #: The list of cuba keys that are available (read only)
    available = Property(Set(CUBATrait), depends_on='_available')

    #: Currently selected CUBA key
    selected = CUBATrait

    #: The dictionary mapping uid to the extracted value.
    data = Property(Dict(UUID, Any), depends_on='_data')

    # Private traits #########################################################

    _available = Set(CUBATrait)

    _data = Dict(UUID, Any)

    # Constructor ############################################################

    def __init__(self, **traits):
        super(CUDSDataExtractor, self).__init__(**traits)
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
        function = self.function
        generator = function(self.keys)
        available = set()
        selected = self.selected
        if selected is None:
            for item in generator:
                available.update(item.data.viewkeys())
        else:
            data = {}
            for item in generator:
                data[item.uid] = item.data.get(selected, None)
                available.update(item.data.viewkeys())
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
