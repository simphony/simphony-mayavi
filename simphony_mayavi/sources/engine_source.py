import logging

from traits.api import Instance, Enum, Str, ListStr, cached_property, Property
from traitsui.api import View, Group, Item, VGroup
from apptools.persistence.state_pickler import set_state

from simphony.cuds.abc_modeling_engine import ABCModelingEngine

from .cuds_source import CUDSSource

logger = logging.getLogger(__name__)


class EngineSource(CUDSSource):
    """ A mayavi source for reading data from a SimPhoNy Engine

    Attributes
    ----------
    engine : Instance
       Simphony modeling engine wrapper
       (Base class: ABCModelingEngine)

    dataset : str
       Selected dataset name in the engine

    Examples
    --------
    >>> source = EngineSource(engine=some_engine)
    >>> source.datasets
    ["particles", "lattice"]
    >>> source.dataset = "particles"

    >>> # Alternatively
    >>> source = EngineSource(engine=some_engine, dataset="particles")

    >>> from mayavi import mlab
    >>> mlab.pipline.glypy(source)
    """
    # The version of this class.  Used for persistence
    __version__ = 0

    # the SimPhoNy Modeling Engine from which datasets are loaded
    engine = Instance(ABCModelingEngine)

    # Label for the engine (for representation purposes)
    engine_name = Str

    # The name of the CUDS container that is currently loaded
    dataset = Enum(values="datasets")

    # datasets depends on the engine and should be read-only
    datasets = Property(ListStr, depends_on="engine")

    view = View(
        VGroup(
            Group(Item(name="dataset")),
            Group(
                Item(name="point_scalars_name"),
                Item(name="point_vectors_name"),
                Item(name="cell_scalars_name"),
                Item(name="cell_vectors_name"),
                Item(name="data"))))

    # Read-only attribute ##################################################

    @cached_property
    def _get_datasets(self):
        '''Available dataset names in the engine'''
        return self.engine.get_dataset_names()

    # Public interface #####################################################

    def start(self):
        """ Load dataset from the engine and start the visualisation """
        # if the EngineSource is restored from saved visualisation
        # `engine` is not defined
        if not self.running and self.engine:
            self._update_cuds()
        super(EngineSource, self).start()

    # Trait Change Handlers ################################################

    def _engine_changed(self):
        # update the cuds if the source is started
        if self.running:
            self._update_cuds()

    def _dataset_changed(self):
        self._update_cuds()

    # Private interface ####################################################

    def _update_cuds(self):
        if self.datasets:
            self.cuds = self.engine.get_dataset(self.dataset)
        else:
            logger.warning("No dataset is available from the engine")

    def _get_name(self):
        """ Returns the name to display on the tree view.  Note that
        this is not a property getter.
        """
        engine_name = self.engine_name or "engine"
        return '{} (CUDS from {})'.format(self.dataset, engine_name)

    def __get_pure_state__(self):
        state = super(EngineSource, self).__get_pure_state__()

        # Skip pickling the engine
        state.pop("engine", None)

        # Remove unselected dataset names from the cache
        state["_traits_cache_datasets"] = [self.dataset]

        logger.warning("The ABCModelingEngine instance is not pickled")
        return state

    def __set_pure_state__(self, state):
        logger.warning(("The ABCModelingEngine instance is not restored. "
                        "Please assign the data source `engine` attribute"))

        # set the dataset names first because data_changed will
        # call _get_name()
        set_state(self, state, first=["_traits_cache_datasets"],
                  ignore=["*"])

        super(EngineSource, self).__set_pure_state__(state)
