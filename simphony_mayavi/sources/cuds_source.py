import logging

from traits.api import Either, Instance, TraitError, Property, HasTraits
from traitsui.api import View, Group, Item
from mayavi.core.api import PipelineInfo
from mayavi.sources.vtk_data_source import VTKDataSource
from simphony.cuds.abc_mesh import ABCMesh
from simphony.cuds.abc_particles import ABCParticles
from simphony.cuds.abc_lattice import ABCLattice
from simphony.io.h5_mesh import H5Mesh

from simphony_mayavi.cuds.api import VTKParticles, VTKLattice, VTKMesh

logger = logging.getLogger(__name__)


class CUDSSource(VTKDataSource):
    """ A mayavi source of a SimPhoNy CUDS container.

    Attributes
    ----------
    cuds : instance of ABCParticle/ABCMesh/ABCLattice/H5Mesh
         The CUDS container to be wrapped as VTK data source

    point_scalars_name : str
         Name of the point scalar array visualised

    point_vectors_name : str
         Name of the point vector array visualised

    cell_scalars_name : str
         Name of the cell scalar array visualised

    cell_vectors_name : str
         Name of the cell vector array visualised


    The ``cuds`` attribute holds a reference to the CUDS instance it is
    assigned to, as oppose to making a copy.  Therefore in any given time
    after setting ``cuds``, the CUDS container could be modified internally
    and divert from the VTK data source.  The ``update`` function can be
    called to update the visualisation.

    Examples
    --------
    >>> cuds = Particles("test")  # the container is empty

    >>> # Say each particle has scalars "TEMPERATURE" and "MASS"
    >>> # and vector data: "VELOCITY"
    >>> cuds.add_particles([...])

    >>> # Initialise the source and specify scalar data to visualise
    >>> # but turn off the visualisation for point vectors
    >>> source = CUDSSource(cuds=cuds, point_scalars="MASS",
                            point_vectors="")

    >>> # Show it in Mayavi!
    >>> from mayavi import mlab
    >>> mlab.pipeline.glyph(source)

    >>> # If the original cuds dataset is modified,
    >>> # you need to update the source
    >>> cuds.add_particles([...])
    >>> source.update()    # the scene is updated
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
        self._update_vtk_cuds_from_cuds(value)

    # Traits change handlers ###############################################

    def __vtk_cuds_changed(self, value):
        self.data = value.data_set

    # Public method ########################################################

    def __init__(self, cuds=None, point_scalars=None, point_vectors=None,
                 cell_scalars=None, cell_vectors=None, **traits):
        """ Constructor

        Parameters
        ----------
        cuds : ABCParticles, ABCLattice, ABCMesh or H5Mesh
            The CUDS dataset to be wrapped as VTK data source

        point_scalars : str
            CUBA name of the data to be selected as point scalars.
            Default is the first available point scalars.

        point_vectors : str
            CUBA name of the data to be selected as point vectors.
            Default is the first available point vectors.

        cell_scalars : str
            CUBA name of the data to be selected as cell scalars.
            Default is the first available cell scalars.

        cell_vectors : str
            CUBA name of the data to be selected as cell vectors.
            Default is the first available cell vectors.

        Notes
        -----
        To turn off visualisation for a point/cell scalar/vector data,
        assign the attribute to an empty string (i.e. point_scalars="")

        Other optional keyword parameters are parsed to VTKDataSource.

        """
        # required by Traits
        super(CUDSSource, self).__init__(**traits)

        if cuds:
            self.cuds = cuds

        # if cuds is not defined, _point_scalars_list (etc.) is empty
        # nothing would be selected
        self._select_attributes(point_scalars=point_scalars,
                                point_vectors=point_vectors,
                                cell_scalars=cell_scalars,
                                cell_vectors=cell_vectors)

    def update(self):
        """ Recalculate the VTK data from the CUDS dataset
        Useful when ``cuds`` is modified after assignment
        """
        self._update_vtk_cuds_from_cuds(self.cuds)

    # Private interface ####################################################

    def _select_attributes(self, point_scalars=None, point_vectors=None,
                           cell_scalars=None, cell_vectors=None):
        """ Select point_scalars/point_vectors/cell_scalars/cell_vectors
        for the CUDSSource

        If point_scalars/... is undefined, the first available attribute
        is selected by mayavi.core.trait_defs.DEnum (see VTKDataSource)
        """
        if self._point_scalars_list and point_scalars is not None:
            self.point_scalars_name = point_scalars

        if self._point_vectors_list and point_vectors is not None:
            self.point_vectors_name = point_vectors

        if self._cell_scalars_list and cell_scalars is not None:
            self.cell_scalars_name = cell_scalars

        if self._cell_vectors_list and cell_vectors is not None:
            self.cell_vectors_name = cell_vectors

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

    def _update_vtk_cuds_from_cuds(self, cuds):
        """ update _vtk_cuds. """
        if isinstance(cuds, (VTKMesh, VTKParticles, VTKLattice)):
            vtk_cuds = cuds
        else:
            if isinstance(cuds, (ABCMesh, H5Mesh)):
                vtk_cuds = VTKMesh.from_mesh(cuds)
            elif isinstance(cuds, ABCParticles):
                vtk_cuds = VTKParticles.from_particles(cuds)
            elif isinstance(cuds, ABCLattice):
                vtk_cuds = VTKLattice.from_lattice(cuds)
            else:
                msg = 'Provided object {} is not of any known cuds type'
                raise TraitError(msg.format(type(cuds)))
        self._vtk_cuds = vtk_cuds

    def __get_pure_state__(self):
        state = super(CUDSSource, self).__get_pure_state__()

        # Skip pickling CUDS dataset
        state.pop("_cuds", None)
        state.pop("_vtk_cuds", None)

        logger.warning("The data is pickled but original CUDS dataset is not.")
        return state

    def __set_pure_state__(self, state):
        logger.warning(("The data is restored but the original "
                        "CUDS dataset is not. "
                        "Please assign the data source `cuds` attribute."))
        super(CUDSSource, self).__set_pure_state__(state)
