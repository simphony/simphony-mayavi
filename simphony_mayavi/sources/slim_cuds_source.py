import itertools

from mayavi.core.source import Source
from mayavi.sources.vtk_data_source import has_attributes
from mayavi.sources.vtk_xml_file_reader import get_all_attributes
from mayavi.core.trait_defs import DEnum
from mayavi.core.pipeline_info import (PipelineInfo,
                                       get_tvtk_dataset_name)

from tvtk.common import is_old_pipeline
from tvtk.api import tvtk
from tvtk import messenger
from traits.api import TraitError, Instance, Either, Property, List, Str, \
    Int, Dict
from traitsui.api import View, Group, Item

from simphony.core.cuba import CUBA
from simphony.core.keywords import KEYWORDS
from simphony.cuds import ABCMesh, ABCParticles, ABCLattice
from simphony.io.h5_mesh import H5Mesh
from simphony_mayavi.cuds.vtk_lattice import VTKLattice
from simphony_mayavi.cuds.vtk_mesh import VTKMesh
from simphony_mayavi.cuds.vtk_particles import VTKParticles


def data_type_attrs():
    """Returns a convenient iterable for data_type
    entries ("point", "cell") and attributes ("scalars", "vectors").
    """
    return itertools.product(["point", "cell"], ["scalars", "vectors"])


class SlimCUDSSource(Source):
    """Overrides Source to provide a source optimized for lower memory
    consumption, sacrificing access speed.
    This is achieved by retrieving data as they are requested by the user,
    instead of preemptively load all available data.
    """
    # More info:
    # This class basic working mechanics performs the following transformation:
    #
    # CUDS -> vtk cuds -> vtk dataset -> adjust vtk pipeline
    #
    # This results in updating the pipeline and finally showing the selection.
    #
    # Differently from VTKDataSource, the CUDS -> vtk cuds transformation
    # involves only the data that are requested, so the vtk dataset
    # content is minimal and according to the user selection.

    #: The version of this class. Used for persistence.
    __version__ = 0

    #: The CUDS container
    cuds = Property(depends_on='_cuds')

    #: Datatype enums. These enumerations contain the allowed CUBA data
    #: as strings and the selected one out of the list. The corresponding
    #: selection is contained into the private _point_scalar_list etc.
    #: traits.
    #: NOTE: these names must not change, as they are computed dynamically.
    point_scalars_name = DEnum(values_name='_point_scalars_list',
                               desc='scalar point data attribute to use')
    point_vectors_name = DEnum(values_name='_point_vectors_list',
                               desc='vectors point data attribute to use')
    cell_scalars_name = DEnum(values_name='_cell_scalars_list',
                              desc='scalar cell data attribute to use')
    cell_vectors_name = DEnum(values_name='_cell_vectors_list',
                              desc='vectors cell data attribute to use')

    #: Output information for the processing pipeline.
    #: Overridden from the base class for more specialized setup.
    output_info = PipelineInfo(
        datasets=['image_data', 'poly_data', 'unstructured_grid'],
        attribute_types=['any'],
        attributes=['scalars', 'vectors'])

    # The View to present in mayavi pane.
    view = View(
        Group(
            Item(name='point_scalars_name'),
            Item(name='point_vectors_name'),
            Item(name='cell_scalars_name'),
            Item(name='cell_vectors_name'),
            Item(name='data')))

    # The VTK dataset to manage. It is taken from the vtk_cuds.
    # Name is unfortunately generic, but is for compatibility with
    # CUDSSource. It is unsure if it needs to be public at all.
    data = Property(Instance(tvtk.DataSet), depends_on="_vtk_cuds")

    # Private traits #############################

    # These private traits store the list of available data
    # attributes for the above x_y_name enumeration.
    #: NOTE: these names must not change, as they are computed dynamically.
    _point_scalars_list = List(Str)
    _point_vectors_list = List(Str)
    _point_tensors_list = List(Str)
    _cell_scalars_list = List(Str)
    _cell_vectors_list = List(Str)
    _cell_tensors_list = List(Str)

    #: This dictionary stores the user selected defaults as specified
    #: at constructor. Differently from CUDSSource, this information is
    #: required so that we can distinguish between an empty name that is empty
    #: because no explicit default was specified and an empty name that is due
    #: to the user actually setting the empty choice as default
    #: Keys are "point_scalars", "point_vectors" etc. values are the default
    #: as specified at construction.
    _constructor_default_names = Dict(Str, Either(Str, None))

    #: The shadow trait for the cuds property.
    _cuds = Either(
        Instance(ABCMesh),
        Instance(H5Mesh),
        Instance(ABCParticles),
        Instance(ABCLattice))

    #: The VTK backed CUDS container
    _vtk_cuds = Either(
        Instance(VTKMesh),
        Instance(VTKParticles),
        Instance(VTKLattice))

    # This filter allows us to change the attributes of the data
    # object and will ensure that the pipeline is properly taken care
    # of.  Directly setting the array in the VTK object will not do
    # this.
    _assign_attribute = Instance(tvtk.AssignAttribute, args=(),
                                 allow_none=False)

    # The ID of the observer for the data.
    _observer_id = Int(-1)

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

        Examples
        --------
        >>> cuds = Particles("test")

        >>> # Say each particle has scalars "TEMPERATURE" and "MASS"
        >>> # and vector data: "VELOCITY"
        >>> cuds.add_particles([...])

        >>> # Initialise the source and specify scalar data to visualise
        >>> # but turn off the visualisation for point vectors
        >>> source = SlimCUDSSource(
                        cuds=cuds,
                        point_scalars="MASS",
                        point_vectors="")

        >>> # Show it in Mayavi!
        >>> from mayavi import mlab
        >>> mlab.pipeline.glyph(source)
        """
        super(SlimCUDSSource, self).__init__(**traits)

        # I don't want to use locals(). Too risky.
        arguments = {
            "point_scalars": point_scalars,
            "point_vectors": point_vectors,
            "cell_scalars": cell_scalars,
            "cell_vectors": cell_vectors
        }

        defaults = {}
        for data_type_attr in ["{}_{}".format(data_type, attr)
                               for data_type, attr in data_type_attrs()]:
            defaults[data_type_attr] = arguments[data_type_attr]

        self._constructor_default_names = defaults

        if cuds:
            self.cuds = cuds

    # Public
    # -------------------------------------------------------------------------

    def start(self):
        """This is invoked when this object is added to the mayavi
        pipeline.
        """
        if self.running:
            return

        self._do_full_refresh()

        super(SlimCUDSSource, self).start()

    def update(self):
        """ Recalculate the VTK data from the CUDS dataset
        Useful when ``cuds`` is modified after assignment
        """
        self._do_full_refresh()

    # Properties
    # -------------------------------------------------------------------------

    def _get_cuds(self):
        return self._cuds

    def _set_cuds(self, cuds):
        """Sets the new cuds, and updates the pipeline appropriately"""
        self._cuds = cuds
        self._do_full_refresh()

        # Change our name according to the nature of the new cuds,
        # so that our label on the tree is updated.
        self.name = self._get_name()

    def _get_data(self):
        return self._vtk_cuds.data_set

    # Change handlers
    # -------------------------------------------------------------------------

    # Triggered when the user selects a new entry from the comboboxes
    def _point_scalars_name_changed(self, value):
        self._update_vtk_cuds_from_cuds()

    def _point_vectors_name_changed(self, value):
        self._update_vtk_cuds_from_cuds()

    def _cell_scalars_name_changed(self, value):
        self._update_vtk_cuds_from_cuds()

    def _cell_vectors_name_changed(self, value):
        self._update_vtk_cuds_from_cuds()
    ###

    def _data_changed(self, old, new):
        """When the vtk dataset changes, adjust the pipeline
        accordingly so that we sync against the new dataset"""

        if has_attributes(self.data):
            aa = self._assign_attribute
            self.configure_input_data(aa, new)
            self._update_vtk_dataset_content()
            aa.update()
            self.outputs = [aa.output]
        else:
            self.outputs = [self.data]

        # Notify the pipeline to refresh against the new data.
        self.data_changed = True

        self.output_info.datasets = \
            [get_tvtk_dataset_name(self.outputs[0])]

        # Add an observer to the VTK dataset after removing the one
        # for the old dataset.  We use the messenger to avoid an
        # uncollectable reference cycle.  See the
        # tvtk.messenger module documentation for details.
        if old is not None:
            old.remove_observer(self._observer_id)
        self._observer_id = new.add_observer('ModifiedEvent',
                                             messenger.send)
        new_vtk = tvtk.to_vtk(new)
        messenger.connect(new_vtk,
                          'ModifiedEvent',
                          self._fire_data_changed)

    # Private
    # -------------------------------------------------------------------------

    def _do_full_refresh(self):
        """Performs appropriate refresh against the current cuds data,
        and chooses the appropriate defaults considering the current
        selected combobox names (if present), or the defaults specified
        at construction"""

        current_names = self._collect_current_names()

        self._fill_datatype_enums()
        self._select_names_silently(
            default_names=self._constructor_default_names,
            current_names=current_names,
        )
        self._update_vtk_cuds_from_cuds()

    def _fill_datatype_enums(self):
        """Fills the "comboboxes" enumeration options from the current cuds.
        Works appropriately if the cuds is None.

        Note that after filling the comboboxes, the selected entry is enforced
        to the empty selection "". This is because we want to postpone this
        selection to have more flexibility and reduce wasted setting
        as much as possible.
        """
        cuds = self.cuds
        available_keys = _available_keys(cuds) if cuds is not None else {}

        # We go through the individual combobox lists, computing their names
        # and using reflection, populating each _list with the keys available,
        # adding a space for "no selection" and finally setting the appropriate
        # default in the _name trait
        for data_type, attr in data_type_attrs():
            data_type_attr = "{}_{}".format(data_type, attr)
            keys = available_keys.get(data_type_attr, set())
            entries = sorted([key.name for key in keys])

            # Add an empty entry so that we always have something to
            # select, and selecting this one will disable the visualization
            # of that dataset.
            entries.append('')

            # Set the list content for the enumeration
            lst = getattr(self, "_{}_list".format(data_type_attr))
            lst[:] = entries

            # we want to set it silently, because
            # otherwise it would trigger the update of the vtk cuds,
            # and we are not ready to do so in most circumstances.
            # Later, the update of the vtk cuds will use the value
            # to present the correct entry
            self.trait_setq(
                **{"{}_name".format(data_type_attr): ""}
            )

    def _collect_current_names(self):
        """Retrieves the current combobox selection, and returns a dictionary
        for each of the keys "point_scalars", "point_vectors" etc...

        Important to note is that if there are no available options in the
        _list entries, the current name will be None, not ''. It will be
        '' only if this entry is actually available and selected in the
        combobox.
        """
        result = {}

        for data_type, attr in data_type_attrs():
            data_type_attr = "{}_{}".format(data_type, attr)
            name = getattr(self, "{}_name".format(data_type_attr))
            available = getattr(self, "_{}_list".format(data_type_attr))

            if name not in available:
                name = None

            result[data_type_attr] = name

        return result

    def _select_names_silently(self, default_names, current_names):
        """Decides, and set silently, the names to select according
        to the current available entries in the _lists, the default
        as specified at construction, and the names that were selected
        before the change"""

        for data_type, attr in data_type_attrs():
            data_type_attr = "{}_{}".format(data_type, attr)
            default = default_names[data_type_attr]
            previous = current_names[data_type_attr]
            currently_available = getattr(self,
                                          "_{}_list".format(data_type_attr))

            if previous in currently_available:
                selected = previous
            elif default in currently_available:
                selected = default
            else:
                selected = currently_available[0]

            self.trait_setq(
                **{"{}_name".format(data_type_attr): selected}
            )

    def _update_vtk_cuds_from_cuds(self):
        """This private method converts the CUDS into a VTKCUDS.
        The VTKCUDS contains a VTK DataSet (accessible through the
        _vtk_dataset property) that contains only the data currently
        selected via the selection comboboxes.

        It is generally used when
        - the cuds change, or
        - the selection in the comboboxes change
        """
        cuds = self.cuds
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
                vtk_cuds = VTKParticles.from_particles(cuds, points_keys,
                                                       cell_keys)
            elif isinstance(cuds, ABCLattice):
                vtk_cuds = VTKLattice.from_lattice(cuds, points_keys)
            else:
                msg = 'Provided object {} is not of any known cuds type'
                raise TraitError(msg.format(type(cuds)))

        # Finally set the vtk cuds. This will update self.data as a
        # subsequent handler.
        self._vtk_cuds = vtk_cuds

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

    def _fire_data_changed(self, *args):
        """Simply fire the `data_changed` event."""
        self.data_changed = True

    ###########
    # Synchronization routines for the vtk dataset changes and the
    # overall low-level vtk pipeline. Used by _data_changed
    def _update_vtk_dataset_content(self):
        vtk_dataset = self.data

        if vtk_dataset is None:
            return

        pnt_attr, cell_attr = get_all_attributes(vtk_dataset)

        scalars = vtk_dataset.point_data.scalars
        if vtk_dataset.is_a('vtkImageData') and scalars is not None:
            # For some reason getting the range of the scalars flushes
            # the data through to prevent some really strange errors
            # when using an ImagePlaneWidget.
            if is_old_pipeline():
                self._assign_attribute.output.scalar_type = scalars.data_type
                vtk_dataset.scalar_type = scalars.data_type

        self._update_vtk_pipeline_for_data('point', pnt_attr)
        self._update_vtk_pipeline_for_data('cell', cell_attr)

    def _update_vtk_pipeline_for_data(self, data_type, attributes):
        """Support routine to setup the appropriate pipeline objects.
        """
        # e.g. self.data.point_data
        data_type_data = getattr(self.data, '%s_data' % data_type)

        assign_attribute = self._assign_attribute
        for attr in ['scalars', 'vectors']:
            values = attributes[attr]
            if len(values) > 0:
                # We should have only one by design, so we set this one
                # as active
                value = values[0]

                # e.g. point_data.set_active_scalar
                set_active_attr = getattr(data_type_data,
                                          'set_active_%s' % attr)
                set_active_attr(value)

                assign_attribute.assign(value, attr.upper(),
                                        data_type.upper() + '_DATA')
                assign_attribute.update()
    ##########

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


def _available_keys(cuds):
    """Given a cuds, it returns a dict of sets, containing the available
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
    _ : dict(key: set)
        A dict of sets for each of the classes above, with the corresponding
        keys as above.
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

    return {
        "point_scalars": point_scalars,
        "point_vectors": point_vectors,
        "cell_scalars": cell_scalars,
        "cell_vectors": cell_vectors
    }


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
