
from traits.api import Either, Instance, TraitError, Property
from traitsui.api import View, Group, Item
from mayavi.core.api import PipelineInfo
from mayavi.sources.vtk_data_source import VTKDataSource
from simphony.cuds.abc_mesh import ABCMesh
from simphony.cuds.abc_particles import ABCParticles
from simphony.cuds.abc_lattice import ABCLattice
from simphony.io.h5_mesh import H5Mesh

from simphony_mayavi.cuds.api import VTKParticles, VTKLattice, VTKMesh


class CUDSSource(VTKDataSource):
    """ A mayavi source of a SimPhoNy CUDS container.

    Attributes
    ----------
    cuds : instance of ABCParticle/ABCMesh/ABCLattice/H5Mesh
         The CUDS container to be wrapped as VTK data source

    The ``cuds`` attribute holds a reference to the CUDS instance it is
    assigned to, as oppose to making a copy.  Therefore in any given time
    after setting ``cuds``, the CUDS container could be modified internally
    and divert from the VTK data source.  The ``update`` function can be
    called to update the visualisation.

    Examples
    --------
    >>> cuds = Particles("test")  # the container is empty
    >>> source = CUDSSource(cuds=cuds)

    # Add content to cuds after the source is initialised
    >>> cuds.add_particles([...])

    >>> from mayavi import mlab
    >>> mlab.pipeline.glyph(source)   # scene is empty
    >>> source.update()    # particles are shown!
    """
    #: The version of this class. Used for persistence.
    __version__ = 1

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

    view = View(
        Group(
            Item(name='point_scalars_name'),
            Item(name='point_vectors_name'),
            Item(name='cell_scalars_name'),
            Item(name='cell_vectors_name'),
            Item(name='data')))

    # Property get/set/validate methods ######################################

    def _get_cuds(self):
        return self._cuds

    def _set_cuds(self, value):
        self._cuds = value
        self._set_vtk_cuds(value)

    # Traits change handlers ###############################################

    def __vtk_cuds_changed(self, value):
        self.data = value.data_set

    # Public method ########################################################

    def update(self):
        """ Recalculate the VTK data from the CUDS dataset
        Useful when ``cuds`` is modified after assignment """
        self._set_vtk_cuds(self.cuds)

    # Private interface ####################################################

    def _get_name(self):
        """ Returns the name to display on the tree view.  Note that
        this is not a property getter.
        """
        cuds = self.cuds
        if isinstance(cuds, (ABCMesh, H5Mesh)):
            name = cuds.name
            kind = u'CUDS Mesh'
        elif isinstance(cuds, ABCParticles):
            name = cuds.name
            kind = u'CUDS Particles'
        elif isinstance(cuds, ABCLattice):
            name = cuds.name
            kind = u'CUDS Lattice'
        else:
            name = u'Uninitialised'
            kind = u'Unknown'
        return '{} ({})'.format(name, kind)

    def _set_vtk_cuds(self, value):
        """ update _vtk_cuds.  Note that this is not a property setter """
        if isinstance(value, (VTKMesh, VTKParticles, VTKLattice)):
            vtk_cuds = value
        else:
            if isinstance(value, (ABCMesh, H5Mesh)):
                vtk_cuds = VTKMesh.from_mesh(value)
            elif isinstance(value, ABCParticles):
                vtk_cuds = VTKParticles.from_particles(value)
            elif isinstance(value, ABCLattice):
                vtk_cuds = VTKLattice.from_lattice(value)
            else:
                msg = 'Provided object {} is not of any known cuds type'
                raise TraitError(msg.format(type(value)))
        self._vtk_cuds = vtk_cuds
