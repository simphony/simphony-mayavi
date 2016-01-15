from traits.api import Instance, Enum, Str
from traitsui.api import View, Group, Item, VGroup

from simphony.cuds.abc_modeling_engine import ABCModelingEngine

from .cuds_source import CUDSSource


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
    @property
    def datasets(self):
        '''Available dataset names in the engine'''
        return self.engine.get_dataset_names()

    # Public interface #####################################################

    def start(self):
        """ Load dataset from the engine and start the visualisation """
        if not self.running:
            self.cuds = self.engine.get_dataset(self.dataset)
        super(EngineSource, self).start()

    # Trait Change Handlers ################################################

    def _dataset_changed(self):
        self.cuds = self.engine.get_dataset(self.dataset)

    # Private interface ####################################################

    def _get_name(self):
        """ Returns the name to display on the tree view.  Note that
        this is not a property getter.
        """
        engine_name = self.engine_name or "engine"
        return '{} (CUDS from {})'.format(self.dataset, engine_name)
