from itertools import count

import numpy

from mayavi.sources.vtk_data_source import VTKDataSource
from tvtk.api import tvtk
from traits.api import Dict

from simphony_mayavi.core.api import (
    CELL2VTKCELL, FACE2VTKCELL, EDGE2VTKCELL,
    CUBADataAccumulator, gather_cells)


class MeshSource(VTKDataSource):
    """ SimPhoNy CUDS Mesh container to Mayavi Source converter

    """

    #: The mapping from the point uid to the vtk points array.
    point2index = Dict

    #: The mapping from the element uid to the vtk cell index.
    element2index = Dict

    @classmethod
    def from_mesh(cls, mesh):
        """ Return a MeshSource from a CUDS Mesh container.

        Parameters
        ----------
        mesh : Mesh
            The CUDS Mesh instance to copy the information from.

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
        data = tvtk.UnstructuredGrid(points=points)
        data.set_cells(element_types, cell_offset, cell_array)

        point_data.load_onto_vtk(data.point_data)
        cell_data.load_onto_vtk(data.cell_data)

        return cls(
            data=data,
            point2index=point2index,
            element2index=element2index)
