from contextlib import closing
import logging

from traits.api import ListStr, Instance
from traitsui.api import View, Group, Item, VGroup
from apptools.persistence.file_path import FilePath
from mayavi.core.trait_defs import DEnum
from simphony.io.h5_cuds import H5CUDS

from .cuds_source import CUDSSource

logger = logging.getLogger(__name__)


class CUDSFileSource(CUDSSource):
    """ A mayavi source of a SimPhoNy CUDS File.

    """
    #: The version of this class. Used for persistence.
    __version__ = 0

    #: The file path of the cuds file to read.
    file_path = Instance(FilePath, (''), desc='the current file name')

    #: The name of the CUDS container that is currently loaded.
    dataset = DEnum(values_name='datasets')

    #: The names of the contained datasets.
    datasets = ListStr

    view = View(
        VGroup(
            Group(Item(name='dataset')),
            Group(
                Item(name='point_scalars_name'),
                Item(name='point_vectors_name'),
                Item(name='cell_scalars_name'),
                Item(name='cell_vectors_name'),
                Item(name='data'))))

    # Public interface #####################################################

    def initialize(self, filename):
        """ Initialise the CUDS file source.
        """
        self.file_path = FilePath(filename)
        with closing(H5CUDS.open(filename)) as handle:
            names = [container.name for container in handle.iter_datasets()]
        if len(names) == 0:
            logger.warning('No datasets found in: %s', self.file_path)
        self.datasets = names

    def start(self):
        if not self.running:
            self.update()
        super(CUDSFileSource, self).start()

    def update(self):
        dataset = self.dataset
        with closing(H5CUDS.open(str(self.file_path))) as handle:
            try:
                self.cuds = handle.get_dataset(dataset)
            except ValueError as ex:
                logger.warning(ex.message)

    # Trait Change Handlers ################################################

    def _dataset_changed(self):
        self.update()

    # Private interface ####################################################

    def _get_name(self):
        """ Returns the name to display on the tree view.  Note that
        this is not a property getter.
        """
        name = super(CUDSFileSource, self)._get_name()
        return 'CUDS File: ' + name
