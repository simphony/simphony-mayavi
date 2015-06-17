from itertools import count

import numpy

from mayavi.sources.vtk_data_source import VTKDataSource
from tvtk.api import tvtk
from traits.api import Dict

from .cuds_data_accumulator import CUDSDataAccumulator
from simphony_mayavi.core.api import CELL2VTKCELL, FACE2VTKCELL, EDGE2VTKCELL


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

        point_data = CUDSDataAccumulator()
        cell_data = CUDSDataAccumulator()

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


def gather_cells(
        iterable, vtk_mapping, point2index, counter, accumulator):
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

    accumulator : CUDSDataAccumulator
        The accumulator instance to use and collect the data information

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
        accumulator.append(element.data)

    return cells, cells_size, cell_types, element2index
