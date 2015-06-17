import uuid
import contextlib
import copy

from tvtk.api import tvtk

from simphony.cuds.abstractmesh import ABCMesh
from simphony.cuds.mesh import Point, Edge, Face, Cell
from simphony.core.data_container import DataContainer
from simphony_mayavi.core.api import (
    CubaData, CellCollection, supported_cuba, mergedocs,
    EDGE2VTKCELL, FACE2VTKCELL, CELL2VTKCELL,
    ELEMENT2VTKCELLTYPES, VTKCELLTYPE2ELEMENT)


@mergedocs(ABCMesh)
class VTKMesh(ABCMesh):

    def __init__(self, name, data=None, data_set=None):
        self.name = name
        self._data = DataContainer() if data is None else DataContainer(data)
        #: The mapping from uid to point index
        self.point2index = {}
        #: The reverse mapping from index to point uid
        self.index2point = {}
        #: The mapping from uid to bond index
        self.element2index = {}
        #: The reverse mapping from index to bond uid
        self.index2element = {}

        # Setup the data_set
        if data_set is None:
            points = tvtk.Points()
            # Need to initialise lines with empty so that we
            # do not get the shared CellArray
            data_set = tvtk.UnstructuredGrid(points=points)
        else:
            for index in xrange(data_set.number_of_points):
                uid = uuid.uuid4()
                self.point2index[uid] = index
                self.index2point[index] = uid
            for index in xrange(data_set.number_of_cells):
                uid = uuid.uuid4()
                self.element2index[uid] = index
                self.index2element[index] = uid

        #: The vtk.PolyData dataset
        self.data_set = data_set

        #: The currently supported and stored CUBA keywords.
        self.supported_cuba = supported_cuba()

        #: Easy access to the vtk PointData structure
        data = data_set.point_data
        if data.number_of_arrays == 0:
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
        self.element_data = CubaData(
            data, stored_cuba=self.supported_cuba, size=size)

        # Elements cells
        self.elements = CellCollection(data_set.get_cells())

    @property
    def data(self):
        """ The container data
        """
        return DataContainer(self._data)

    @data.setter
    def data(self, value):
        self._data = DataContainer(value)

    # Point operations ####################################################

    def add_point(self, point):
        data_set = self.data_set
        points = data_set.points
        point2index = self.point2index
        with self._add_item(point, point2index) as item:
            index = points.insert_next_point(item.coordinates)
            point2index[item.uid] = index
            self.index2point[index] = item.uid
            self.point_data.append(item.data)
            return item.uid

    def get_point(self, uid):
        if not isinstance(uid, uuid.UUID):
            raise TypeError("{} is not a uuid".format(uid))
        index = int(self.point2index[uid])
        return Point(
            uid=uid,
            coordinates=self.data_set.points[index],
            data=self.point_data[index])

    def update_point(self, point):
        try:
            index = self.point2index[point.uid]
        except KeyError:
            message = "Point with {} does exist"
            raise ValueError(message.format(point.uid))
        # Need to cast to int https://github.com/enthought/mayavi/issues/173
        self.data_set.points[int(index)] = point.coordinates
        self.point_data[index] = point.data

    def iter_points(self, uids=None):
        if uids is None:
            for uid in self.point2index:
                yield self.get_point(uid)
        else:
            for uid in uids:
                yield self.get_point(uid)

    # special private ########################################################

    def _update_element(self, element):
        try:
            index = self.element2index[element.uid]
        except KeyError:
            message = "{} with {} does exist"
            raise ValueError(message.format(type(element), element.uid))
        point_ids = [self.point2index[uid] for uid in element.points]
        self.elements[index] = point_ids
        self.element_data[index] = element.data

    # Edge operations ########################################################

    def get_edge(self, uid):
        if not isinstance(uid, uuid.UUID):
            raise TypeError("{} is not a uuid".format(uid))
        index = self.element2index[uid]
        return self._get_element(index, Edge)

    def has_edges(self):
        return self._has_elements(Edge)

    def iter_edges(self, uids=None):
        if uids is None:
            for edge in self._iter_elements(Edge):
                yield edge
        else:
            for uid in uids:
                yield self.get_edge(uid)

    def add_edge(self, edge):
        return self._add_element(edge, mapping=EDGE2VTKCELL)

    update_edge = copy.copy(_update_element)

    # Face operations ########################################################

    def get_face(self, uid):
        if not isinstance(uid, uuid.UUID):
            raise TypeError("{} is not a uuid".format(uid))
        index = self.element2index[uid]
        return self._get_element(index, Face)

    def has_faces(self):
        return self._has_elements(Face)

    def iter_faces(self, uids=None):
        if uids is None:
            for face in self._iter_elements(Face):
                yield face
        else:
            for uid in uids:
                yield self.get_face(uid)

    def add_face(self, face):
        return self._add_element(face, mapping=FACE2VTKCELL)

    update_face = copy.copy(_update_element)

    # Cell operations ########################################################

    def get_cell(self, uid):
        if not isinstance(uid, uuid.UUID):
            raise TypeError("{} is not a uuid".format(uid))
        index = self.element2index[uid]
        return self._get_element(index, Cell)

    def has_cells(self):
        return self._has_elements(Cell)

    def iter_cells(self, uids=None):
        if uids is None:
            for cell in self._iter_elements(Cell):
                yield cell
        else:
            for uid in uids:
                yield self.get_cell(uid)

    def add_cell(self, cell):
        return self._add_element(cell, mapping=CELL2VTKCELL)

    update_cell = copy.copy(_update_element)

    # Private interface ######################################################

    @contextlib.contextmanager
    def _add_item(self, item, container):
        if item.uid is None:
            item.uid = uuid.uuid4()
        elif item.uid in container:
            message = "Item with id:{} already exists"
            raise ValueError(message.format(item.uid))
        yield item

    def _has_elements(self, element):
        cell_types = self.data_set.cell_types_array
        for type_ in ELEMENT2VTKCELLTYPES[element]:
            if type_ in cell_types:
                return True
        else:
            return False

    def _get_element(self, index, type_=None):
        data_set = self.data_set
        element = data_set.get_cell(index)
        if type_ is None:
            type_ = VTKCELLTYPE2ELEMENT[data_set.get_cell_type(index)]
        return type_(
            uid=self.index2element[index],
            points=[self.index2point[i] for i in element.point_ids],
            data=self.element_data[index])

    def _iter_elements(self, type_):
        cell_types = self.data_set.cell_types_array
        types = ELEMENT2VTKCELLTYPES[type_]
        index2point = self.index2point
        index2element = self.index2element
        element_data = self.element_data
        data_set = self.data_set
        for index, cell_type in enumerate(cell_types):
            if cell_type in types:
                element = data_set.get_cell(index)
                yield type_(
                    uid=index2element[index],
                    points=[index2point[i] for i in element.point_ids],
                    data=element_data[index])

    def _add_element(self, element, mapping):
        data_set = self.data_set
        element2index = self.element2index
        with self._add_item(element, element2index) as item:
            point_ids = [self.point2index[uid] for uid in item.points]
            index = data_set.insert_next_cell(
                mapping[len(point_ids)], point_ids)
            element2index[item.uid] = index
            self.index2element[index] = item.uid
            self.element_data.append(item.data)
            return item.uid
