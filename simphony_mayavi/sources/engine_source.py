
from traits.api import ListStr, Instance, Property, cached_property
from traitsui.api import View, Group, Item, VGroup
from mayavi.core.trait_defs import DEnum

from simphony.cuds.abc_modeling_engine import ABCModelingEngine

from .cuds_source import CUDSSource


class EngineSource(CUDSSource):
    """ A mayavi source for reading data from a SimPhoNy Engine
    """
    # the SimPhoNy Modeling Engine from which datasets are loaded
    engine = Property(depends_on="_engine")

    _engine = Instance(ABCModelingEngine)

    # The name of the CUDS container that is currently loaded
    dataset = DEnum(values_name="datasets")

    # The names of the datasets in the engine
    datasets = ListStr

    view = View(
        VGroup(
            Group(Item(name="dataset")),
            Group(
                Item(name="point_scalars_name"),
                Item(name="point_vectors_name"),
                Item(name="cell_scalars_name"),
                Item(name="cell_vectors_name"),
                Item(name="cell_vectors_name"),
                Item(name="data"))))

    @cached_property
    def _get_engine(self):
        return self._engine

    def _set_engine(self, value):
        self._engine = value
        self.datasets = value.get_dataset_names()

    def start(self):
        if not self.running:
            self.update()
        super(EngineSource, self).start()

    def update(self):
        self.cuds = self.engine.get_dataset(self.dataset)

    def _dataset_changed(self):
        self.update()

    def _get_name(self):
        """ Returns the name to display on the tree view.  Note that
        this is not a property getter.
        """
        name = super(CUDSSource, self)._get_name()
        return 'Engine CUDS: {} ({})'.format(self.dataset, name)
