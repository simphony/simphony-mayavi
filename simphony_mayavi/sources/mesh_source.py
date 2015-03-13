from collections import defaultdict
from itertools import count

import numpy

from mayavi.sources.vtk_data_source import VTKDataSource
from tvtk.api import tvtk
from traits.api import Dict

CELL2VTKCELL = {
    4: tvtk.Tetra().cell_type,
    8: tvtk.Hexahedron().cell_type,
    6: tvtk.Wedge().cell_type,
    5: tvtk.Pyramid().cell_type,
    10: tvtk.PentagonalPrism().cell_type,
    12: tvtk.HexagonalPrism().cell_type}

_polygon_type = tvtk.Polygon().cell_type
_polyline_type = tvtk.PolyLine().cell_type

FACE2VTKCELL = defaultdict(
    lambda: _polygon_type,
    {3: tvtk.Triangle().cell_type, 4: tvtk.Quad().cell_type})

EDGE2VTKCELL = defaultdict(
    lambda: _polyline_type, {2: tvtk.Line().cell_type})


class MeshSource(VTKDataSource):
    """ A Mayavi Source wrapping a SimPhoNy CUDS Mesh container.

    """

    #: The mapping from the point uid to the vtk polydata points array.
    point2index = Dict

    #: The mapping from the element uid to the vtk polydata cell index.
    element2index = Dict

    @classmethod
    def from_mesh(cls, mesh):
        points = []
        point2index = {}
        element2index = {}
        counter = count()

        for index, point in enumerate(mesh.iter_points()):
            point2index[point.uid] = index
            points.append(point.coordinates)

        edges, edges_size, edge_types, edge2index = gather_cells(
            mesh.iter_edges(), EDGE2VTKCELL, point2index, counter)

        faces, faces_size, face_types, face2index = gather_cells(
            mesh.iter_faces(), FACE2VTKCELL, point2index, counter)

        cells, cells_size, cell_types, cell2index = gather_cells(
            mesh.iter_cells(), CELL2VTKCELL, point2index, counter)

        elements = edges + faces + cells
        elements_size = [0] + edges_size + faces_size + cells_size
        element_types = edge_types + face_types + cell_types
        element2index.update(edge2index)
        element2index.update(face2index)
        element2index.update(cell2index)

        cell_offset = numpy.cumsum(elements_size[:-1])
        cell_array = tvtk.CellArray()
        cell_array.set_cells(len(cell_offset), elements)
        data = tvtk.UnstructuredGrid(points=points)
        data.set_cells(element_types, cell_offset, cell_array)

        return cls(
            data=data,
            point2index=point2index,
            element2index=element2index)


def gather_cells(iterable, vtk_mapping, point2index, counter):
    """ Gather the vtk cell information from an element iterator.

    Arguments
    ---------
    iterable :
        The Element iterable object

    mapping : dict
        The mapping from points number to tvtk.Cell type.

    point2index: dict
        The mapping from points uid to the index of the vtk points array.

    index : itertools.count
        The counter object to use when evaluating the ``elements2index``
        mapping.

    Returns
    -------
    cells : list
         The cell point information encoded in a one dimensional list.

    cells_size : list
         The list of points number per cell.

    cells_types : list
         The list of cell types in sequence.

    element2index : dict
         The mapping from element uid to iteration index.

    """
    cells = []
    cells_size = []
    cell_types = []
    element2index = {}

    for element in iter(iterable):
        element2index[element.uid] = counter.next()
        npoints = len(element.points)
        cells_size.append(npoints + 1)
        cells.append(npoints)
        cells.extend(point2index[uid] for uid in element.points)
        cell_types.append(vtk_mapping[npoints])

    return cells, cells_size, cell_types, element2index
