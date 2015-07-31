
from traits.api import Either, Instance, TraitError, Property, cached_property
from mayavi.core.api import PipelineInfo
from mayavi.sources.vtk_data_source import VTKDataSource
from simphony.cuds.abstractmesh import ABCMesh
from simphony.cuds.abstractparticles import ABCParticles
from simphony.cuds.abstractlattice import ABCLattice
from simphony.io.h5_mesh import H5Mesh

from simphony_mayavi.cuds.api import VTKParticles, VTKLattice, VTKMesh


class CUDSSource(VTKDataSource):
    """ A mayavi source of a SimPhoNy CUDS container.

    """
    #: The version of this class. Used for persistence.
    __version__ = 0

    #: The CUDS container
    cuds = Property(depends_on='_cuds')

    #: Output information for the processing pipeline.
    output_info = PipelineInfo(
        datasets=['image_data', 'poly_data', 'unstructured_grid'],
        attribute_types=['any'],
        attributes=['scalars', 'vectors'])

    #: The shadow trait for the cuds property
    _cuds = Either(
        Instance(ABCMesh),
        Instance(H5Mesh),
        Instance(ABCParticles),
        Instance(ABCLattice))

    #: The shadow VTK backed CUDS container
    _vtk_cuds = Either(
        Instance(VTKMesh),
        Instance(VTKParticles),
        Instance(VTKLattice))

    # Property get/set/validate methods ######################################

    @cached_property
    def _get_cuds(self):
        return self._cuds

    def _set_cuds(self, value):
        if isinstance(value, (VTKMesh, VTKParticles, VTKLattice)):
            cuds = value
            vtk_cuds = value
        else:
            cuds = value
            if isinstance(value, (ABCMesh, H5Mesh)):
                vtk_cuds = VTKMesh.from_mesh(value)
            elif isinstance(value, ABCParticles):
                vtk_cuds = VTKParticles.from_particles(value)
            elif isinstance(value, ABCLattice):
                vtk_cuds = VTKLattice.from_lattice(value)
            else:
                msg = 'Provided object {} is not of any known cuds type'
                raise TraitError(msg.format(type(value)))
        self._cuds = cuds
        self._vtk_cuds = vtk_cuds

    # Traits change handlers \\\\\\\\\######################################

    def __vtk_cuds_changed(self, value):
        self.data = value.data_set
