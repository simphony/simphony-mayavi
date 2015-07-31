from contextlib import closing

from traits.api import Instance, Either, Str, List
from apptools.persistence.file_path import FilePath
from tvtk.api import tvtk
from mayavi.core.api import PipelineInfo
from mayavi.core.trait_defs import DEnum
from simphony.cuds.abstractmesh import ABCMesh
from simphony.cuds.abstractparticles import ABCParticles
from simphony.cuds.abstractlattice import ABCLattice
from simphony.io.h5_cuds import H5CUDS
from simphony.io.h5_mesh import H5Mesh

from .cuds_source import CUDSSource


class CUDSFileSource(CUDSSource):
    """ A mayavi source of a SimPhoNy CUDS File.

    """
    #: The version of this class. Used for persistence.
    __version__ = 0

    #: The file path of the cuds file to read.
    file_path = Instance(FilePath, (' '), desc='the current file name')

    #: The name of the CUDS container that is currently loaded.
    dataset = Either(Str, None)

    #: The names of the contained datasets.
    datasets = List(Str)

    # Public interface #####################################################
    def initialize(self, filename):
        """ Initialise the CUDS file source.
        """
        self.file_path = FilePath(filename)
        with closing(H5CUDS.open(filename)) as handle:
            names = [container.name for container in handle.iter_particles()]
            names += [container.name for container in handle.iter_lattices()]
            names += [container.name for container in handle.iter_meshes()]
        self.datasets = names
        if self.dataset is None:
            self.dataset = names[0]

    def update(self):
        dataset = self.dataset
        if dataset is None:
            raise RuntimeError('A dataset name is required')
        else:
            with closing(H5CUDS.open(str(self.file_path))) as handle:
                for container in ['particles', 'lattice', 'mesh']:
                    method = getattr(handle, 'get_{}'.format(container))
                    try:
                        container = method(dataset)
                    except ValueError:
                        continue
                    else:
                        self.cuds = container
                        break
                else:
                    message = 'A dataset "{}" was not found'
                    raise RuntimeError(message.format(dataset))
