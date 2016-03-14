import itertools

from tvtk.common import is_old_pipeline
from mayavi.sources.vtk_xml_file_reader import get_all_attributes
from traits.api import TraitError

from simphony.core.cuba import CUBA
from simphony.core.keywords import KEYWORDS
from simphony.cuds import ABCMesh, ABCParticles, ABCLattice
from simphony.io.h5_mesh import H5Mesh
from simphony_mayavi.cuds.vtk_lattice import VTKLattice
from simphony_mayavi.cuds.vtk_mesh import VTKMesh
from simphony_mayavi.cuds.vtk_particles import VTKParticles
from simphony_mayavi.sources.cuds_source import CUDSSource


class SlimCUDSSource(CUDSSource):
    """Overrides CUDSSource to provide a source optimized for lower memory
    consumption, sacrificing access speed.
    This is achieved by retrieving data as they are requested by the user,
    instead of preemptively load all available data.
    """

    def _point_scalars_name_changed(self, value):
        self.update()

    def _point_vectors_name_changed(self, value):
        self.update()

    def _cell_scalars_name_changed(self, value):
        self.update()

    def _cell_vectors_name_changed(self, value):
        self.update()

    def _set_cuds(self, cuds):
        # Before refreshing the VTK CUDS object, we need to set the content
        # of the available data in the cuds. Normally this is done by the
        # VTKDataSource _from_ the VTK data, but our VTK data will not contain
        # all the keys. We are therefore required to update them here.
        all_lists = (
            self._point_scalars_list,
            self._point_vectors_list,
            self._cell_scalars_list,
            self._cell_vectors_list)

        for lst, keys in zip(all_lists, _available_keys(cuds)):
            lst[:] = sorted([key.name for key in keys])
            # Adds an empty string as selection for not show attribute
            lst.insert(0, '')

        # We need to fill the tensors with an empty entry, even if we
        # technically don't use them.
        self._point_tensors_list = ['']
        self._cell_tensors_list = ['']

        super(SlimCUDSSource, self)._set_cuds(cuds)

    def _update_vtk_cuds_from_cuds(self, cuds):
        """Update _vtk_cuds, but limit the extraction to only the requested
        data."""

        # Extract the requested data we want.
        points_keys = [CUBA[x]
                       for x in [self.point_scalars_name,
                                 self.point_vectors_name]
                       if len(x) > 0]

        cell_keys = [CUBA[x]
                     for x in [self.cell_scalars_name,
                               self.cell_vectors_name]
                     if len(x) > 0]

        if isinstance(cuds, (VTKMesh, VTKParticles, VTKLattice)):
            vtk_cuds = cuds
        else:
            if isinstance(cuds, (ABCMesh, H5Mesh)):
                vtk_cuds = VTKMesh.from_mesh(cuds, points_keys, cell_keys)
            elif isinstance(cuds, ABCParticles):
                vtk_cuds = VTKParticles.from_particles(
                    cuds,
                    points_keys,
                    cell_keys)
            elif isinstance(cuds, ABCLattice):
                vtk_cuds = VTKLattice.from_lattice(
                    cuds,
                    points_keys)
            else:
                msg = 'Provided object {} is not of any known cuds type'
                raise TraitError(msg.format(type(cuds)))
        self._vtk_cuds = vtk_cuds

    def _update_data(self):
        """Reimplement _update_data from VTKDataSource,
        to workaround its automatic rewriting of names in the data.
        The e.g. _point_scalars_list is filled with the VTK dataset info
        by this method, but by design of this class, the VTK dataset content
        is limited. We need to take full control of those lists while leaving
        the rest of the method functionality alone.
        """

        if self.data is None:
            return
        pnt_attr, cell_attr = get_all_attributes(self.data)

        pd = self.data.point_data
        scalars = pd.scalars
        if self.data.is_a('vtkImageData') and scalars is not None:
            # For some reason getting the range of the scalars flushes
            # the data through to prevent some really strange errors
            # when using an ImagePlaneWidget.
            if is_old_pipeline():
                self._assign_attribute.output.scalar_type = scalars.data_type
                self.data.scalar_type = scalars.data_type

        self._setup_data_traits(pnt_attr, 'point')
        self._setup_data_traits(cell_attr, 'cell')

        if self._first:
            self._first = False

        # Propagate the data changed event.
        self.data_changed = True

    def __get_pure_state__(self):
        """Overrides the same functionality from the base class, but
        since it is based on the vtk content, which is restricted, we can't
        provide this functionality on this class"""
        raise NotImplementedError("Cannot get state of SlimCUDSSource. "
                                  "Operation not implemented.")

    def __set_pure_state__(self, state):
        """Overrides the same functionality from the base class, but
        since it is based on the vtk content, which is restricted, we can't
        provide this functionality on this class"""
        raise NotImplementedError("Cannot set state of SlimCUDSSource. "
                                  "Operation not implemented.")

    def _setup_data_traits(self, attributes, d_type):
        """Given the object, the dict of the attributes from the
        `get_all_attributes` function and the data type
        (point/cell) data this will setup the object and the data.
        """
        attrs = ['scalars', 'vectors', 'tensors']
        aa = self._assign_attribute
        data = getattr(self.data, '%s_data' % d_type)
        for attr in attrs:
            values = attributes[attr]
            if len(values) == 0:
                choice = ''
            else:
                choice = getattr(self, '%s_%s_name' % (d_type, attr))

            getattr(data, 'set_active_%s' % attr)(choice)
            aa.assign(choice, attr.upper(), d_type.upper() + '_DATA')
            aa.update()
            kw = {'%s_%s_name' % (d_type, attr): choice,
                  'trait_change_notify': False}
            self.set(**kw)


def _available_keys(cuds):
    """Given a cuds, it returns a tuple of sets, containing the available
    CUBA keys divided in classes:

        - point_scalars
        - point_vectors
        - cell_scalars
        - cell_vectors

    Parameters
    ----------
    cuds :
        A cuds data source

    Returns
    -------
    _ : tuple(set, set, set, set)
        A tuple of four sets for each of the classes above.
    """

    point_scalars = set()
    point_vectors = set()
    cell_scalars = set()
    cell_vectors = set()

    if isinstance(cuds, (ABCMesh, H5Mesh)):
        for point in cuds.iter_points():
            scalar_keys, vector_keys = _extract_cuba_keys_per_data_types(
                point.data)
            point_scalars.update(scalar_keys)
            point_vectors.update(vector_keys)

        for element in itertools.chain(cuds.iter_cells(),
                                       cuds.iter_edges(),
                                       cuds.iter_faces()):
            scalar_keys, vector_keys = _extract_cuba_keys_per_data_types(
                element.data)
            cell_scalars.update(scalar_keys)
            cell_vectors.update(vector_keys)

    elif isinstance(cuds, ABCParticles):
        for particle in cuds.iter_particles():
            scalar_keys, vector_keys = _extract_cuba_keys_per_data_types(
                particle.data)
            point_scalars.update(scalar_keys)
            point_vectors.update(vector_keys)

        for bond in cuds.iter_bonds():
            scalar_keys, vector_keys = _extract_cuba_keys_per_data_types(
                bond.data)
            cell_scalars.update(scalar_keys)
            cell_vectors.update(vector_keys)

    elif isinstance(cuds, ABCLattice):
        for node in cuds.iter_nodes():
            scalar_keys, vector_keys = _extract_cuba_keys_per_data_types(
                node.data)
            point_scalars.update(scalar_keys)
            point_vectors.update(vector_keys)

    else:
        msg = 'Provided object {} is not of any known cuds type'
        raise TraitError(msg.format(type(cuds)))

    return point_scalars, point_vectors, cell_scalars, cell_vectors


def _extract_cuba_keys_per_data_types(data_container):
    """Given a DataContainer, gets the scalar and vector CUBA types
    it contains, as two independent sets

    Parameters
    ----------
    data_container : DataContainer
        A data container.

    Returns
    -------
    scalars, vectors : tuple(set, set)
        The CUBA type keys for scalar and vector data, respectively
    """
    scalars = set()
    vectors = set()

    for cuba_key in data_container.keys():
        shape = KEYWORDS[cuba_key.name].shape

        if shape == [1]:
            scalars.add(cuba_key)
        elif shape == [3]:
            vectors.add(cuba_key)
        else:
            # We don't represent this dimensionality, skip it
            pass

    return scalars, vectors
