import sys
import uuid
import contextlib

from tvtk.api import tvtk

from simphony.core.cuba import CUBA
from simphony.cuds.abc_particles import ABCParticles
from simphony.core.cuds_item import CUDSItem
from simphony.cuds.particles import Particle, Bond
from simphony.core.data_container import DataContainer
from simphony_mayavi.core.api import (
    CubaData, CellCollection, supported_cuba, mergedocs,
    CUBADataAccumulator, VTKEDGETYPES)


@mergedocs(ABCParticles)
class VTKParticles(ABCParticles):

    def __init__(self, name, data=None, data_set=None, mappings=None):
        """ Constructor.

        Parameters
        ----------
        name : string
            The name of the container.

        data : DataContainer
            The data attribute to attach to the container. Default is None.

        data_set : tvtk.DataSet
            The dataset to wrap in the CUDS api. Default is None which
            will create a tvtk.PolyData

        mappings : dict
            A dictionary of mappings for the particle2index, index2particle,
            bond2index and bond2element. Should be provided if the particles
            and bonds described in ``data_set`` are already assigned uids.
            Default is None and will result in the uid <-> index mappings being
            generated at construction.

        """
        self.name = name
        self._data = DataContainer() if data is None else DataContainer(data)
        #: The mapping from uid to point index
        self.particle2index = {}
        #: The reverse mapping from index to point uid
        self.index2particle = {}
        #: The mapping from uid to bond index
        self.bond2index = {}
        #: The reverse mapping from index to bond uid
        self.index2bond = {}

        self._items_count = {
            CUDSItem.PARTICLE: lambda: self.particle2index,
            CUDSItem.BOND: lambda: self.bond2index
        }

        # Setup the data_set
        if data_set is None:
            points = tvtk.Points()
            # Need to initialise lines with empty so that we
            # do not get the shared CellArray
            data_set = tvtk.PolyData(points=points, lines=[])
            # To use get_cell we need to have at least one point in the
            # dataset.
            points.append((0.0, 0.0, 0.0))
            self.initialized = True
        else:
            self.initialized = False
            if mappings is None:
                for index in xrange(data_set.number_of_points):
                    uid = uuid.uuid4()
                    self.particle2index[uid] = index
                    self.index2particle[index] = uid
                for index in xrange(data_set.number_of_cells):
                    uid = uuid.uuid4()
                    self.bond2index[uid] = index
                    self.index2bond[index] = uid
            else:
                self.particle2index = mappings['particle2index']
                self.bond2index = mappings['bond2index']
                self.index2particle = mappings['index2particle']
                self.index2bond = mappings['index2bond']

        #: The vtk.PolyData dataset
        self.data_set = data_set

        #: The currently supported and stored CUBA keywords.
        self.supported_cuba = supported_cuba()

        #: Easy access to the vtk PointData structure
        data = data_set.point_data
        if data.number_of_arrays == 0 and not self.initialized:
            size = data_set.number_of_points
        else:
            size = None
        self.point_data = CubaData(
            data, stored_cuba=self.supported_cuba, size=size)

        #: Easy access to the vtk CellData structure
        data = data_set.cell_data
        ncells = data_set.number_of_cells
        if data.number_of_arrays == 0 and ncells != 0:
            size = ncells
        else:
            size = None
        self.bond_data = CubaData(
            data, stored_cuba=self.supported_cuba, size=size)

        #: Easy access to the lines vtk CellArray structure
        if hasattr(data_set, 'lines'):
            self.bonds = CellCollection(data_set.lines)
        else:
            self.bonds = CellCollection(data_set.get_cells())

    @property
    def data(self):
        """ The container data
        """
        return DataContainer(self._data)

    @data.setter
    def data(self, value):
        self._data = DataContainer(value)

    @classmethod
    def from_particles(cls, particles):
        """ Create a new VTKParticles copy from a CUDS particles instance.

        """
        points = []
        lines = []
        particle2index = {}
        bond2index = {}
        index2particle = {}
        index2bond = {}
        particle_data = CUBADataAccumulator()
        bond_data = CUBADataAccumulator()

        for index, particle in enumerate(particles.iter_particles()):
            uid = particle.uid
            particle2index[uid] = index
            index2particle[index] = uid
            points.append(particle.coordinates)
            particle_data.append(particle.data)
        for index, bond in enumerate(particles.iter_bonds()):
            uid = bond.uid
            bond2index[uid] = index
            index2bond[index] = uid
            lines.append([particle2index[uuid] for uuid in bond.particles])
            bond_data.append(bond.data)

        if len(points) != 0:
            data_set = tvtk.PolyData(points=points, lines=lines)
            particle_data.load_onto_vtk(data_set.point_data)
            bond_data.load_onto_vtk(data_set.cell_data)
        else:
            data_set = None

        mappings = {
            'index2particle': index2particle,
            'particle2index': particle2index,
            'index2bond': index2bond,
            'bond2index': bond2index}

        return cls(
            name=particles.name,
            data=particles.data,
            data_set=data_set,
            mappings=mappings)

    @classmethod
    def from_dataset(cls, name, data_set, data=None):
        """ Wrap a plain dataset into a new VTKParticles.

        The constructor makes some sanity checks to make sure that
        the tvtk.DataSet is compatible and all the information can
        be properly used.

        Raises
        ------
        TypeError :
            When the sanity checks fail.

        """
        checks = []

        # Check for cell related attributes
        checks.append(
            not hasattr(data_set, 'lines')
            and not hasattr(data_set, 'get_cells'))

        # Check that the data set contains only lines and polyline cells
        if hasattr(data_set, 'lines'):
            checks.append(
                data_set.number_of_cells != data_set.lines.number_of_cells)
        if hasattr(data_set, 'get_cells'):
            checks.append(
                not set(data_set.cell_types_array).issubset(set(VTKEDGETYPES)))

        if any(checks):
            message = (
                'Dataset {} cannot be reliably wrapped into a VTKParticles')
            raise TypeError(message.format(data_set))
        return cls(name, data_set=data_set, data=data)

    # Particle operations ####################################################

    def add_particles(self, particles):
        data_set = self.data_set
        points = data_set.points
        particle2index = self.particle2index
        item_uids = []
        for particle in particles:
            with self._add_item(particle, particle2index) as item:
                if self.initialized:
                    # We remove the dummy point
                    self.data_set.points = tvtk.Points()
                    points = data_set.points
                    self.initialized = False
                index = points.insert_next_point(item.coordinates)
                particle2index[item.uid] = index
                self.index2particle[index] = item.uid
                self.point_data.append(item.data)
                item_uids.append(item.uid)

        # adding new points causes the cached array under
        # tvtk.array_handler to be inconsistent with the
        # points FloatArray, therefore we need to remove
        # the reference in the tvtk.array_handler._array_cache
        # for points.to_array() to work properly
        _array_cache = None
        for name in ['array_handler', 'tvtk.array_handler']:
            if sys.modules.has_key(name):
                mod = sys.modules[name]
                if hasattr(mod, '_array_cache'):
                    _array_cache = mod._array_cache
                break
        if _array_cache:
            _array_cache._remove_array(tvtk.to_vtk(points.data).__this__)

        return item_uids

    def get_particle(self, uid):
        index = int(self.particle2index[uid])
        return Particle(
            uid=uid,
            coordinates=self.data_set.points[index],
            data=self.point_data[index])

    def remove_particles(self, uids):
        particle2index = self.particle2index
        index2particle = self.index2particle
        points = self.data_set.points
        point_data = self.point_data

        # keep a counter in case uids is a generator
        # it is used for resizing data_set.points in batch
        count = 0

        for uid in uids:
            # move uid item to the end
            self._swap_with_last(
                uid, particle2index, index2particle,
                points, point_data)
            index = particle2index[uid]

            # remove last point info
            del self.point_data[index]

            # remove uid item from mappings
            del particle2index[uid]
            del index2particle[index]
            count += 1

        array = points.to_array()
        self.data_set.points = array[:-count]
        assert len(self.data_set.points) == len(particle2index)

    def update_particles(self, particles):
        for particle in particles:
            try:
                index = self.particle2index[particle.uid]
            except KeyError:
                message = "Particle with {} does exist"
                raise ValueError(message.format(particle.uid))
            self.data_set.points[index] = particle.coordinates
            self.point_data[index] = particle.data

    def iter_particles(self, uids=None):
        if uids is None:
            for uid in self.particle2index:
                yield self.get_particle(uid)
        else:
            for uid in uids:
                yield self.get_particle(uid)

    def has_particle(self, uid):
        return uid in self.particle2index

    # Bond operations ########################################################

    def is_connected(self, bond):
        """ Test if the connectivity described in bonds is valid
        i.e. the particles are part of the container

        Parameters
        ----------
        bond : Bond

        Returns
        -------
        valid : bool
        """
        return all((self.has_particle(uid) for uid in bond.particles))

    def add_bonds(self, bonds):
        data_set = self.data_set
        bond2index = self.bond2index
        item_uids = []
        for bond in bonds:
            with self._add_item(bond, bond2index) as item:
                if not self.is_connected(bond):
                    message = "Cannot add Bond {} with missing uids: {}"
                    raise ValueError(message.format(item.uid, item.particles))
                point_ids = [self.particle2index[uid] for uid in item.particles]
                index = data_set.insert_next_cell(VTKEDGETYPES[1], point_ids)
                bond2index[item.uid] = index
                self.index2bond[index] = item.uid
                self.bond_data.append(item.data)
                item_uids.append(item.uid)
        return item_uids

    def get_bond(self, uid):
        index = self.bond2index[uid]

        # cannot use self.data_set.get_cell(index) here because
        # get_cell would give the wrong point_ids if the dimension
        # of the cell changes upon update
        point_ids = self.bonds[index]
        return Bond(
            uid=uid,
            particles=[self.index2particle[i] for i in point_ids],
            data=self.bond_data[index])

    def update_bonds(self, bonds):
        for bond in bonds:
            if not self.is_connected(bond):
                message = "Cannot update Bond {} with missing uids: {}"
                raise ValueError(message.format(bond.uid, bond.particles))
            try:
                index = self.bond2index[bond.uid]
            except KeyError:
                message = "Bond with {} does not exist"
                raise ValueError(message.format(bond.uid))
            point_ids = [self.particle2index[uid] for uid in bond.particles]
            self.bonds[index] = point_ids
            self.bond_data[index] = bond.data

    def has_bond(self, uid):
        return uid in self.bond2index

    def remove_bonds(self, uids):
        bond2index = self.bond2index
        index2bond = self.index2bond
        bond_data = self.bond_data
        bonds = self.bonds

        for uid in uids:
            # move uid item to the end
            self._swap_with_last(
                uid, bond2index, index2bond, bonds, bond_data)
            index = bond2index[uid]

            # remove last bond info
            del bonds[index]
            del bond_data[index]

            # remove uid item from mappings
            del bond2index[uid]
            del index2bond[index]

    def iter_bonds(self, uids=None):
        if uids is None:
            for uid in self.bond2index:
                yield self.get_bond(uid)
        else:
            for uid in uids:
                yield self.get_bond(uid)

    def count_of(self, item_type):
        try:
            return len(self._items_count[item_type]())
        except KeyError:
            error_str = "Trying to obtain count a of non-supported item: {}"
            raise ValueError(error_str.format(item_type))

    # Private interface ######################################################

    @contextlib.contextmanager
    def _add_item(self, item, container):
        if item.uid is None:
            item.uid = uuid.uuid4()
        elif item.uid in container:
            message = "Item with id:{} already exists"
            raise ValueError(message.format(item.uid))
        yield item

    def _swap_with_last(self, uid, mapping, reverse_mapping, items, data):
        """ Swap the entries of uid item with the last item in the data_set

        Parameters
        ----------
        uid : uuid.UUID
            The uid of the item to move last.
        mapping : dict
            The mapping from uid to index.
        reverse_mapping : dict
            The reverse mapping from index to uid.
        items : sequence
            The sequence of items
        data : CubaData
            The associated CubaData instance

        """
        index = mapping[uid]
        last_index = len(mapping) - 1
        last_uid = reverse_mapping[last_index]
        mapping[last_uid], mapping[uid] = index, last_index
        reverse_mapping[index], reverse_mapping[last_index] = last_uid, uid
        data[last_index], data[index] = data[index], data[last_index]
        items[last_index], items[index] = items[index], items[last_index]
