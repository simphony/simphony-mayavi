from collections import defaultdict

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

FACE2VTKCELL = defaultdict(
    lambda: tvtk.Polygon().cell_type,
    {3: tvtk.Triangle().cell_type, 4: tvtk.Quad().cell_type})

EDGE2VTKCELL = defaultdict(
    lambda: tvtk.PolyLine().cell_type, {2: tvtk.Line().cell_type})


class MeshSource(VTKDataSource):
    """ A Mayavi Source wrapping a SimPhoNy CUDS Particle container.

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
        for index, point in enumerate(mesh.iter_points()):
            point2index[point.uid] = index
            points.append(point.coordinates)

        cells = []
        cells_size = [0]
        cell_types = []

        for index, edge in enumerate(mesh.iter_edges()):
            element2index[edge.uid] = index
            npoints = len(edge.points)
            cells_size.append(npoints + 1)
            cells.append(npoints)
            cells.extend(point2index[uid] for uid in edge.points)
            cell_types.append(EDGE2VTKCELL[npoints])

        for index, face in enumerate(mesh.iter_faces()):
            element2index[face.uid] = index
            npoints = len(face.points)
            cells_size.append(npoints + 1)
            cells.append(npoints)
            cells.extend(point2index[uid] for uid in face.points)
            cell_types.append(FACE2VTKCELL[npoints])

        for index, cell in enumerate(mesh.iter_cells()):
            element2index[cell.uid] = index
            npoints = len(cell.points)
            cells_size.append(npoints + 1)
            cells.append(npoints)
            cells.extend(point2index[uid] for uid in cell.points)
            cell_types.append(CELL2VTKCELL[npoints])

        offset = numpy.cumsum(cells_size[:-1])
        cell_array = tvtk.CellArray()
        cell_array.set_cells(len(offset), cells)
        data = tvtk.UnstructuredGrid(points=points)
        data.set_cells(cell_types, offset, cell_array)
        return cls(
            data=data,
            point2index=point2index,
            element2index=element2index)
