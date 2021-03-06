from numpy import array

from simphony.cuds.mesh import Mesh, Point, Cell, Edge, Face
from simphony.core.data_container import DataContainer


points = array([
    [0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1],
    [2, 0, 0], [3, 0, 0], [3, 1, 0], [2, 1, 0],
    [2, 0, 1], [3, 0, 1], [3, 1, 1], [2, 1, 1]],
    'f')

cells = [
    [0, 1, 2, 3],  # tetra
    [4, 5, 6, 7, 8, 9, 10, 11]]  # hex

faces = [[2, 7, 11]]
edges = [[1, 4], [3, 8]]

mesh = Mesh('example')

# add points
point_iter = (Point(coordinates=point, data=DataContainer(TEMPERATURE=index))
              for index, point in enumerate(points))
uids = mesh.add(point_iter)

# add edges
edge_iter = (Edge(points=[uids[index] for index in element])
             for index, element in enumerate(edges))
edge_uids = mesh.add(edge_iter)

# add faces
face_iter = (Face(points=[uids[index] for index in element])
             for index, element in enumerate(faces))
face_uids = mesh.add(face_iter)

# add cells
cell_iter = (Cell(points=[uids[index] for index in element])
             for index, element in enumerate(cells))
cell_uids = mesh.add(cell_iter)


if __name__ == '__main__':
    from simphony.visualisation import mayavi_tools

    # Visualise the Mesh object
    mayavi_tools.show(mesh)
