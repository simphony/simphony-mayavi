import itertools
import numpy
from traits.api import TraitError

from simphony.core.cuba import CUBA
from simphony.cuds import ABCMesh, ABCParticles, ABCLattice
from simphony.io.h5_mesh import H5Mesh
from simphony.testing.utils import dummy_cuba_value
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
        super(CUDSSource, self)._point_scalars_name_changed(value)
        self.update()

    def _point_vectors_name_changed(self, value):
        super(CUDSSource, self)._point_vectors_name_changed(value)
        self.update()

    def _cell_scalars_name_changed(self, value):
        super(CUDSSource, self)._cell_scalars_name_changed(value)
        self.update()

    def _cell_vectors_name_changed(self, value):
        super(CUDSSource, self)._cell_vectors_name_changed(value)
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

        super(SlimCUDSSource, self)._set_cuds(cuds)

    def _update_vtk_cuds_from_cuds(self, cuds):
        """Update _vtk_cuds, but limit the extraction to only the requested
        data."""

        # Extract the requested data we want.
        points_keys = [CUBA[x]
                       for x in [self.point_scalars_name,
                                 self.point_vectors_name]]

        cell_keys = [CUBA[x]
                     for x in [self.cell_scalars_name,
                               self.cell_vectors_name]]

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
        # We need to silence the behavior of the VTKDataSource, otherwise it
        # will overwrite the point_scalar_list etc. with data from the vtk
        # datasource, which in this case contains only the data we care
        # about.
        pass


def _to_cuba(iterable):
    """Small generator that processes an iterable of strings
    into an iterable of CUBA keys"""
    for elem in iterable:
        try:
            yield CUBA[elem]
        except ValueError:
            pass


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


def _extract_cuba_keys_per_data_types(data):
    """Given a DataContainer, gets the scalar and vector CUBA types
    it contains, as two independent sets

    Parameters
    ----------
    data : DataContainer
        A data container.

    Returns
    -------
    scalars, vectors : tuple(set, set)
        The CUBA type keys for scalar and vector data, respectively
    """
    scalars = set()
    vectors = set()

    for cuba_key in data.keys():
        try:
            dim = _cuba_dimensionality(cuba_key)
        except ValueError:
            continue

        if dim == 0:
            scalars.add(cuba_key)
        elif dim == 3:
            vectors.add(cuba_key)
        else:
            # We don't represent this dimensionality, skip it
            pass

    return scalars, vectors


def _cuba_dimensionality(cuba):
    """Given a cuba type, returns its associated dimensionality.
    Raises ValueError if the dimensionality for that cuba type is unknown.
    A scalar has zero dimensionality.

    Parameters
    ----------

    cuba: CUBA
        The CUBA type enumeration


    Returns
    -------
    dim : int
        The dimensionality of the CUBA type

    """

    default = dummy_cuba_value(cuba)
    if (numpy.issubdtype(type(default), numpy.float) or
            numpy.issubdtype(type(default), numpy.int)):
        return 0
    elif isinstance(default, numpy.ndarray) and default.size == 3:
        return 3
    else:
        raise ValueError("Unknown dimensionality for CUBA {}".format(cuba))
