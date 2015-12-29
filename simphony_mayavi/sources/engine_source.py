import logging

from traits.api import Instance, Property, cached_property, Enum
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
    engine = Property(depends_on="_engine")

    _engine = Instance(ABCModelingEngine)

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

    # Property get/set/validate methods ######################################

    @cached_property
    def _get_engine(self):
        return self._engine

    def _set_engine(self, value):
        self._engine = value
        if len(self.datasets) == 0:
            logging.warning("No datasets found in the given engine")

    @property
    def datasets(self):
        return self.engine.get_dataset_names()

    # Public interface #####################################################
    def __init__(self, engine):
        self.engine = engine

    def start(self):
        """ Load dataset from the engine and start the visualisation """
        if not self.running:
            # Load the dataset from engine
            self.cuds = self.engine.get_dataset(self.dataset)
        super(EngineSource, self).start()

    # Trait Change Handlers ################################################

    def _dataset_changed(self):
        if self.dataset:
            self.cuds = self.engine.get_dataset(self.dataset)
        self.point_scalars_name = ""
        self.point_vectors_name = ""
        self.cell_scalars_name = ""
        self.cell_vectors_name = ""

    # Private interface ####################################################

    def _get_name(self):
        """ Returns the name to display on the tree view.  Note that
        this is not a property getter.
        """
        name = super(CUDSSource, self)._get_name()
        return 'Engine CUDS: {} ({})'.format(self.dataset, name)
