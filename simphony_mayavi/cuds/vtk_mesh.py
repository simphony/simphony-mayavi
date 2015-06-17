import uuid
import contextlib

from tvtk.api import tvtk

from simphony.cuds.abstractmesh import ABCMesh
from simphony.cuds.mesh import Point, Edge, Face, Cell
from simphony.core.data_container import DataContainer
from simphony_mayavi.core.api import (
    CubaData, CellCollection, supported_cuba, mergedocs,
    VTKEDGETYPES, EDGE2VTKCELL, FACE2VTKCELL, VTKFACETYPES,
    VTKCELLTYPES, CELL2VTKCELL)


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

    # Edge operations ########################################################

    def add_edge(self, edge):
        data_set = self.data_set
        element2index = self.element2index
        with self._add_item(edge, element2index) as item:
            point_ids = [self.point2index[uid] for uid in item.points]
            index = data_set.insert_next_cell(
                EDGE2VTKCELL[len(point_ids)], point_ids)
            element2index[item.uid] = index
            self.index2element[index] = item.uid
            self.element_data.append(item.data)
            return item.uid

    def get_edge(self, uid):
        if not isinstance(uid, uuid.UUID):
            raise TypeError("{} is not a uuid".format(uid))
        index = self.element2index[uid]
        edge = self.data_set.get_cell(index)
        return Edge(
            uid=uid,
            points=[self.index2point[i] for i in edge.point_ids],
            data=self.element_data[index])

    def update_edge(self, edge):
        try:
            index = self.element2index[edge.uid]
        except KeyError:
            message = "Edge with {} does exist"
            raise ValueError(message.format(edge.uid))
        point_ids = [self.point2index[uid] for uid in edge.points]
        self.elements[index] = point_ids
        self.element_data[index] = edge.data

    def has_edges(self):
        cell_types = self.data_set.cell_types_array
        for type_ in VTKEDGETYPES:
            if type_ in cell_types:
                return True
        else:
            return False

    def iter_edges(self, uids=None):
        if uids is None:
            cell_types = self.data_set.cell_types_array
            for index, cell_type in enumerate(cell_types):
                if cell_type in VTKEDGETYPES:
                    edge = self.data_set.get_cell(index)
                    yield Edge(
                        uid=self.index2element[index],
                        points=[self.index2point[i] for i in edge.point_ids],
                        data=self.element_data[index])
        else:
            for uid in uids:
                yield self.get_edge(uid)

    # Face operations ########################################################

    def get_face(self, uid):
        if not isinstance(uid, uuid.UUID):
            raise TypeError("{} is not a uuid".format(uid))
        index = self.element2index[uid]
        face = self.data_set.get_cell(index)
        return Face(
            uid=uid,
            points=[self.index2point[i] for i in face.point_ids],
            data=self.element_data[index])

    def add_face(self, face):
        data_set = self.data_set
        element2index = self.element2index
        with self._add_item(face, element2index) as item:
            point_ids = [self.point2index[uid] for uid in item.points]
            index = data_set.insert_next_cell(
                FACE2VTKCELL[len(point_ids)], point_ids)
            element2index[item.uid] = index
            self.index2element[index] = item.uid
            self.element_data.append(item.data)
            return item.uid

    def has_faces(self):
        cell_types = self.data_set.cell_types_array
        for type_ in VTKFACETYPES:
            if type_ in cell_types:
                return True
        else:
            return False

    def update_face(self, face):
        try:
            index = self.element2index[face.uid]
        except KeyError:
            message = "Face with {} does exist"
            raise ValueError(message.format(face.uid))
        point_ids = [self.point2index[uid] for uid in face.points]
        self.elements[index] = point_ids
        self.element_data[index] = face.data

    def iter_faces(self, uids=None):
        if uids is None:
            cell_types = self.data_set.cell_types_array
            for index, cell_type in enumerate(cell_types):
                if cell_type in VTKFACETYPES:
                    face = self.data_set.get_cell(index)
                    yield Face(
                        uid=self.index2element[index],
                        points=[self.index2point[i] for i in face.point_ids],
                        data=self.element_data[index])
        else:
            for uid in uids:
                yield self.get_face(uid)

    # Cell operations ########################################################

    def get_cell(self, uid):
        if not isinstance(uid, uuid.UUID):
            raise TypeError("{} is not a uuid".format(uid))
        index = self.element2index[uid]
        face = self.data_set.get_cell(index)
        return Cell(
            uid=uid,
            points=[self.index2point[i] for i in face.point_ids],
            data=self.element_data[index])

    def add_cell(self, cell):
        data_set = self.data_set
        element2index = self.element2index
        with self._add_item(cell, element2index) as item:
            point_ids = [self.point2index[uid] for uid in item.points]
            index = data_set.insert_next_cell(
                CELL2VTKCELL[len(point_ids)], point_ids)
            element2index[item.uid] = index
            self.index2element[index] = item.uid
            self.element_data.append(item.data)
            return item.uid

    def has_cells(self):
        cell_types = self.data_set.cell_types_array
        for type_ in VTKCELLTYPES:
            if type_ in cell_types:
                return True
        else:
            return False

    def update_cell(self, face):
        try:
            index = self.element2index[face.uid]
        except KeyError:
            message = "Cell with {} does exist"
            raise ValueError(message.format(face.uid))
        point_ids = [self.point2index[uid] for uid in face.points]
        self.elements[index] = point_ids
        self.element_data[index] = face.data

    def iter_cells(self, uids=None):
        if uids is None:
            cell_types = self.data_set.cell_types_array
            for index, cell_type in enumerate(cell_types):
                if cell_type in VTKCELLTYPES:
                    cell = self.data_set.get_cell(index)
                    yield Cell(
                        uid=self.index2element[index],
                        points=[self.index2point[i] for i in cell.point_ids],
                        data=self.element_data[index])
        else:
            for uid in uids:
                yield self.get_cell(uid)

    # Private interface ######################################################

    @contextlib.contextmanager
    def _add_item(self, item, container):
        if item.uid is None:
            item.uid = uuid.uuid4()
        elif item.uid in container:
            message = "Item with id:{} already exists"
            raise ValueError(message.format(item.uid))
        yield item
