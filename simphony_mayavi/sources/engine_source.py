from traits.api import Instance, Enum, Str
from traitsui.api import View, Group, Item, VGroup

from simphony.cuds.abc_modeling_engine import ABCModelingEngine

from .cuds_source import CUDSSource


class EngineSource(CUDSSource):
    """ A mayavi source for reading data from a SimPhoNy Engine

    Attributes
    ----------
    datasets : ListStr
       list of dataset names in the engine
    """
    # the SimPhoNy Modeling Engine from which datasets are loaded
    engine = Instance(ABCModelingEngine)

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

    def _get_cuds(self):
        return self._cuds

    # Read-only attribute ##################################################
    @property
    def datasets(self):
        return self.engine.get_dataset_names()

    # Public interface #####################################################

    def __init__(self, engine):
        self.engine = engine

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
        return 'CUDS {} from engine'.format(self.dataset)
