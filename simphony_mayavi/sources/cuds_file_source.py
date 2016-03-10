from contextlib import closing
import logging

from traits.api import ListStr, Instance, Bool, TraitError, HasTraits
from traitsui.api import View, Group, Item, VGroup
from apptools.persistence.file_path import FilePath
from apptools.persistence.state_pickler import set_state
from mayavi.core.common import handle_children_state
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

    # whether the source is initialized
    initialized = Bool(False)

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

    def __init__(self, **traits):
        """ Create a CUDSFileSource instance

        Example
        -------
        >>> source = CUDSFileSource()
        >>> source.initialize("path/to/cuds_file.cuds")
        """
        # This __init__ function should take no argument in order
        # for it to be used by Mayavi2 application
        # This function overloads CUDSSource.__init__

        # required by Traits:
        super(CUDSFileSource, self).__init__(**traits)

    def initialize(self, filename):
        """ Initialise the CUDS file source.
        """
        self.file_path = FilePath(filename)
        with closing(H5CUDS.open(filename)) as handle:
            names = [container.name for container in handle.iter_datasets()]
        if len(names) == 0:
            logger.warning('No datasets found in: %s', self.file_path)
        self.datasets = names
        self.initialized = True

    def start(self):
        # While restoring visualization in a running mayavi
        # engine, the scene would attempt to `start` its
        # sources.  If the `initialized` flag is not checked,
        # `update` will error.
        if not self.running and self.initialized:
            self.update()
        super(CUDSFileSource, self).start()

    def update(self):
        dataset = self.dataset
        with closing(H5CUDS.open(str(self.file_path))) as handle:
            try:
                self.cuds = handle.get_dataset(dataset)
            except ValueError as exception:
                logger.warning(exception.message)

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

    def __set_pure_state__(self, state):
        """ Attempt to restore the reference to file path """
        # restore the file_path
        # possibly a bug in apptools.persistence.file_path.FilePath
        self.file_path = FilePath("")
        set_state(self.file_path, state.file_path)

        # Load the file and setup the datasets
        self.initialize(str(self.file_path))

        try:
            # restore the selected dataset
            self.dataset = state._dataset
        except TraitError as exception:
            msg = ("Could not restore references for '{dataset}' in {path}\n"
                   "Proceed with restoring the data saved anyway.\n"
                   "Got {error}: {error_msg}")
            logger.warning(msg.format(dataset=state._dataset,
                                      path=str(self.file_path),
                                      error=type(exception).__name__,
                                      error_msg=str(exception)))
            # do not overwrite _dataset and datasets while setting states
            state.pop("_dataset", None)
            state.pop("datasets", None)
            # VTKDataSource will restore the data
            super(CUDSFileSource, self).__set_pure_state__(state)
        else:
            # all is done except for the children
            # Setup the children.
            handle_children_state(self.children, state.children)
            # Set the children's state
            set_state(self, state, first=['children'], ignore=['*'])
