import uuid
import contextlib

from tvtk.api import tvtk

from simphony.cuds.abstractparticles import ABCParticles
from simphony.cuds.particles import Particle, Bond
from simphony.core.data_container import DataContainer
from simphony_mayavi.core.api import CubaData, CellCollection, supported_cuba


VTK_POLY_LINE = 4


class VTKParticles(ABCParticles):

    def __init__(self, name, data=None, data_set=None):
        self.name = name
        self._data = DataContainer() if data is None else DataContainer(data)
        if data_set is None:
            points = tvtk.Points()
            # Need to initialise lines with empty so that we
            # do not get the shared CellArray
            data_set = tvtk.PolyData(points=points, lines=[])
            # To use get_cell we need to have at least one point in the
            # dataset.
            points.append((0, 0, 0))
            self.initialized = True
        #: The vtk.PolyData dataset
        self.data_set = data_set
        #: The mapping from uid to point index
        self.particle2index = {}
        #: The reverse mapping from index to point uid
        self.index2particle = {}
        #: The mapping from uid to bond index
        self.bond2index = {}
        #: The reverse mapping from index to bond uid
        self.index2bond = {}
        #: The reverse mapping from index to bond uid
        self.supported_cuba = supported_cuba
        self.point_data = CubaData(data_set.point_data)
        self.bond_data = CubaData(data_set.cell_data)
        self.bonds = CellCollection(data_set.lines)

    @property
    def data(self):
        return DataContainer(self._data)

    @data.setter
    def data(self, value):
        self._data = DataContainer(value)

    # Particle operations ####################################################

    def add_particle(self, particle):
        data_set = self.data_set
        points = data_set.points
        particle2index = self.particle2index
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
        return item.uid

    def get_particle(self, uid):
        index = int(self.particle2index[uid])
        return Particle(
            uid=uid,
            coordinates=self.data_set.points[index],
            data=self.point_data[index])

    def remove_particle(self, uid):
        particle2index = self.particle2index
        index2particle = self.index2particle
        points = self.data_set.points
        point_data = self.point_data

        # move uid item to the end
        self._swap_with_last(
            uid, particle2index, index2particle,
            points, point_data)
        index = particle2index[uid]

        # remove last point info
        array = points.to_array()
        self.data_set.points = array[:-1]
        del self.point_data[index]

        # remove uid item from mappings
        del particle2index[uid]
        del index2particle[index]
        assert len(self.data_set.points) == len(particle2index)

    def update_particle(self, particle):
        try:
            index = self.particle2index[particle.uid]
        except KeyError:
            message = "Particle with {} does exist"
            raise ValueError(message.format(particle.uid))
        # Need to cast to int https://github.com/enthought/mayavi/issues/173
        self.data_set.points[int(index)] = particle.coordinates
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

    def add_bond(self, bond):
        data_set = self.data_set
        bond2index = self.bond2index
        with self._add_item(bond, bond2index) as item:
            point_ids = [self.particle2index[uid] for uid in item.particles]
            index = data_set.insert_next_cell(VTK_POLY_LINE, point_ids)
            bond2index[item.uid] = index
            self.index2bond[index] = item.uid
            self.bond_data.append(item.data)
        return item.uid

    def get_bond(self, uid):
        index = self.bond2index[uid]
        line = self.data_set.get_cell(index)
        return Bond(
            uid=uid,
            particles=[self.index2particle[i] for i in line.point_ids],
            data=self.bond_data[index])

    def update_bond(self, bond):
        try:
            index = self.bond2index[bond.uid]
        except KeyError:
            message = "Bond with {} does exist"
            raise ValueError(message.format(bond.uid))
        point_ids = [self.particle2index[uid] for uid in bond.particles]
        self.bonds[index] = point_ids
        self.bond_data[index] = bond.data

    def has_bond(self, uid):
        return uid in self.bond2index

    def remove_bond(self, uid):
        bond2index = self.bond2index
        index2bond = self.index2bond
        bond_data = self.bond_data
        bonds = self.bonds

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
        # Need to cast to int https://github.com/enthought/mayavi/issues/173
        index = int(mapping[uid])
        last_index = int(len(mapping) - 1)
        last_uid = reverse_mapping[last_index]
        mapping[last_uid], mapping[uid] = index, last_index
        reverse_mapping[index], reverse_mapping[last_index] = last_uid, uid
        data[last_index], data[index] = data[index], data[last_index]
        items[last_index], items[index] = items[index], items[last_index]
