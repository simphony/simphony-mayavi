from numpy import array, random
from tvtk.api import tvtk
from simphony.core.cuba import CUBA
from simphony.visualisation import mayavi_tools


def create_unstructured_grid(array_name='scalars'):
    points = array(
        [[0, 1.2, 0.6], [1, 0, 0], [0, 1, 0], [1, 1, 1],  # tetra
         [1, 0, -0.5], [2, 0, 0], [2, 1.5, 0], [0, 1, 0],
         [1, 0, 0], [1.5, -0.2, 1], [1.6, 1, 1.5], [1, 1, 1]], 'f')  # Hex
    cells = array(
        [4, 0, 1, 2, 3,  # tetra
         8, 4, 5, 6, 7, 8, 9, 10, 11])  # hex
    offset = array([0, 5])
    tetra_type = tvtk.Tetra().cell_type  # VTK_TETRA == 10
    hex_type = tvtk.Hexahedron().cell_type  # VTK_HEXAHEDRON == 12
    cell_types = array([tetra_type, hex_type])
    cell_array = tvtk.CellArray()
    cell_array.set_cells(2, cells)
    ug = tvtk.UnstructuredGrid(points=points)
    ug.set_cells(cell_types, offset, cell_array)
    scalars = random.random(points.shape[0])
    ug.point_data.scalars = scalars
    ug.point_data.scalars.name = array_name
    scalars = random.random((2, 1))
    ug.cell_data.scalars = scalars
    ug.cell_data.scalars.name = array_name
    return ug

# Create an example
vtk_dataset = create_unstructured_grid()

# Adapt to a mesh by converting the scalars attribute to TEMPERATURE
container = mayavi_tools.adapt2cuds(
    vtk_dataset, 'test',
    rename_arrays={'scalars': CUBA.TEMPERATURE})

if __name__ == '__main__':

    # Visualise the Lattice object
    mayavi_tools.show(container)
