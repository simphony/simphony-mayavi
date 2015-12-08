import uuid
import contextlib
from itertools import count

import numpy
from tvtk.api import tvtk

from simphony.cuds.abc_mesh import ABCMesh
from simphony.core.cuds_item import CUDSItem
from simphony.cuds.mesh import Point, Edge, Face, Cell
from simphony.core.data_container import DataContainer
from simphony_mayavi.core.api import (
    CubaData, CellCollection, supported_cuba, mergedocs,
    EDGE2VTKCELL, FACE2VTKCELL, CELL2VTKCELL,
    ELEMENT2VTKCELLTYPES, VTKCELLTYPE2ELEMENT,
    CUBADataAccumulator, gather_cells)


@mergedocs(ABCMesh)
class VTKMesh(ABCMesh):

    def __init__(self, name, data=None, data_set=None, mappings=None):
        """ Constructor.

        Parameters
        ----------
        name : string
            The name of the container

        data : DataContainer
            The data attribute to attach to the container. Default is None.

        data_set : tvtk.DataSet
            The dataset to wrap in the CUDS api. Default is None which
            will create a tvtk.UnstructuredGrid.

        mappings : dict
            A dictionary of mappings for the point2index, index2point,
            element2index and index2element. Should be provided if the points
            and elements described in ``data_set`` are already assigned uids.
            Default is None and will result in the uid <-> index mappings being
            generated at construction.

        """
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
            data_set = tvtk.UnstructuredGrid(points=points)
        else:
            if mappings is None:
                for index in xrange(data_set.number_of_points):
                    uid = uuid.uuid4()
                    self.point2index[uid] = index
                    self.index2point[index] = uid
                for index in xrange(data_set.number_of_cells):
                    uid = uuid.uuid4()
                    self.element2index[uid] = index
                    self.index2element[index] = uid
            else:
                self.point2index = mappings['point2index']
                self.element2index = mappings['element2index']
                self.index2point = mappings['index2point']
                self.index2element = mappings['index2element']

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

        data = data_set.cell_data
        ncells = data_set.number_of_cells
        if data.number_of_arrays == 0 and ncells != 0:
            size = ncells
        else:
            size = None
        #: Easy access to the vtk CellData structure
        self.element_data = CubaData(
            data, stored_cuba=self.supported_cuba, size=size)

        # Elements cells
        self.elements = CellCollection(data_set.get_cells())

    @classmethod
    def from_mesh(cls, mesh):
        """ Create a new VTKMesh copy from a CUDS mesh instance.

        """
        points = []
        point2index = {}
        element2index = {}
        counter = count()

        point_data = CUBADataAccumulator()
        cell_data = CUBADataAccumulator()

        for index, point in enumerate(mesh.iter_points()):
            point2index[point.uid] = index
            points.append(point.coordinates)
            point_data.append(point.data)

        edges, edges_size, edge_types, edge2index = gather_cells(
            mesh.iter_edges(), EDGE2VTKCELL, point2index, counter, cell_data)

        faces, faces_size, face_types, face2index = gather_cells(
            mesh.iter_faces(), FACE2VTKCELL, point2index, counter, cell_data)

        cells, cells_size, cell_types, cell2index = gather_cells(
            mesh.iter_cells(), CELL2VTKCELL, point2index, counter, cell_data)

        elements = edges + faces + cells
        elements_size = [0] + edges_size + faces_size + cells_size
        element_types = edge_types + face_types + cell_types
        element2index.update(edge2index)
        element2index.update(face2index)
        element2index.update(cell2index)

        cell_offset = numpy.cumsum(elements_size[:-1])
        cell_array = tvtk.CellArray()
        cell_array.set_cells(len(cell_offset), elements)

        if len(points) != 0:
            data_set = tvtk.UnstructuredGrid(points=points)
            data_set.set_cells(element_types, cell_offset, cell_array)
            point_data.load_onto_vtk(data_set.point_data)
            cell_data.load_onto_vtk(data_set.cell_data)
        else:
            data_set = None

        mappings = {
            'index2point': {
                value: key for key, value in point2index.iteritems()},
            'point2index': point2index,
            'index2element': {
                value: key for key, value in element2index.iteritems()},
            'element2index': element2index}

        return cls(
            name=mesh.name,
            data=mesh.data,
            data_set=data_set,
            mappings=mappings)

    @classmethod
    def from_dataset(cls, name, data_set, data=None):
        """ Wrap a plain dataset into a new VTKMesh.

        The constructor makes some sanity checks to make sure that
        the tvtk.DataSet is compatible and all the information can
        be properly used.

        Parameters
        ----------
        name : string
            The name of the container

        data_set : tvtk.DataSet
            The dataset to wrap in the CUDS api. Default is None which
            will create a tvtk.UnstructuredGrid.

        data : DataContainer
            The data attribute to attach to the container. Default is None.

        Raises
        ------
        TypeError :
            When the sanity checks fail.

        """
        checks = []
        checks.append(not hasattr(data_set, 'get_cells'))
        if any(checks):
            message = (
                'Dataset {} cannot be reliably wrapped in to a VTKMesh')
            raise TypeError(message.format(data_set))
        return cls(name, data_set=data_set, data=data)

    @property
    def data(self):
        """ The container data
        """
        return DataContainer(self._data)

    @data.setter
    def data(self, data):
        self._data = DataContainer(data)

    def count_of(self, item_type):
        def count_element(type_):
            # max value of cell_types_array is small enough for
            # bincount to be efficient
            counts = numpy.bincount(self.data_set.cell_types_array)
            type_ids = numpy.array(ELEMENT2VTKCELLTYPES[type_])
            type_ids = type_ids[type_ids < len(counts)]
            return counts[type_ids].sum()

        items_count = {
            CUDSItem.POINT: lambda: self.data_set.number_of_points,
            CUDSItem.EDGE: lambda: count_element(Edge),
            CUDSItem.FACE: lambda: count_element(Face),
            CUDSItem.CELL: lambda: count_element(Cell)
        }

        try:
            return items_count[item_type]()
        except KeyError:
            error_str = "Trying to obtain count a of non-supported item: {}"
            raise ValueError(error_str.format(item_type))

    # Point operations ####################################################

    def add_points(self, points):
        data_set = self.data_set
        own_points = data_set.points
        point2index = self.point2index
        new_uids = []
        for point in points:
            with self._add_item(point, point2index) as item:
                index = own_points.insert_next_point(item.coordinates)
                point2index[item.uid] = index
                self.index2point[index] = item.uid
                self.point_data.append(item.data)
                new_uids.append(item.uid)
        return new_uids

    def get_point(self, uid):
        if not isinstance(uid, uuid.UUID):
            raise TypeError("{} is not a uuid".format(uid))
        index = int(self.point2index[uid])
        return Point(
            uid=uid,
            coordinates=self.data_set.points[index],
            data=self.point_data[index])

    def update_points(self, points):
        for point in points:
            try:
                index = self.point2index[point.uid]
            except KeyError:
                message = "Point with {} does not exist"
                raise ValueError(message.format(point.uid))
            self.data_set.points[index] = point.coordinates
            self.point_data[index] = point.data

    def iter_points(self, uids=None):
        if uids is None:
            for uid in self.point2index:
                yield self.get_point(uid)
        else:
            for uid in uids:
                yield self.get_point(uid)

    # special private ########################################################

    def _update_elements(self, elements):
        for element in elements:
            try:
                index = self.element2index[element.uid]
            except KeyError:
                message = "{} with {} does not exist"
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

    def add_edges(self, edges):
        uids = []
        for edge in edges:
            uids.append(self._add_element(edge, mapping=EDGE2VTKCELL))
        return uids

    def update_edges(self, edges):
        return self._update_elements(edges)

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

    def add_faces(self, faces):
        uids = []
        for face in faces:
            uids.append(self._add_element(face, mapping=FACE2VTKCELL))
        return uids

    def update_faces(self, faces):
        return self._update_elements(faces)

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

    def add_cells(self, cells):
        uids = []
        for cell in cells:
            uids.append(self._add_element(cell, mapping=CELL2VTKCELL))
        return uids

    def update_cells(self, cells):
        return self._update_elements(cells)

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
        if type_ is None:
            type_ = VTKCELLTYPE2ELEMENT[data_set.get_cell_type(index)]

        # data_set.get_cell may return the wrong point ids
        # if the cell type is updated
        # Use elements[index] to retrieve point ids instead
        # https://github.com/simphony/simphony-mayavi/issues/94
        return type_(
            uid=self.index2element[index],
            points=[self.index2point[i] for i in self.elements[index]],
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
