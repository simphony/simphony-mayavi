from numpy import array
from mayavi.scripts import mayavi2

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

container = Mesh('test')

# add points
point_iter = (Point(coordinates=point, data=DataContainer(TEMPERATURE=index))
              for index, point in enumerate(points))
uids = container.add_points(point_iter)

# add edges
edge_iter = (Edge(points=[uids[index] for index in element],
                  data=DataContainer(TEMPERATURE=index + 20))
             for index, element in enumerate(edges))
edge_uids = container.add_edges(edge_iter)

# add faces
face_iter = (Face(points=[uids[index] for index in element],
                  data=DataContainer(TEMPERATURE=index + 30))
             for index, element in enumerate(faces))
face_uids = container.add_faces(face_iter)

# add cells
cell_iter = (Cell(points=[uids[index] for index in element],
                  data=DataContainer(TEMPERATURE=index + 40))
             for index, element in enumerate(cells))
cell_uids = container.add_cells(cell_iter)


# Now view the data.
@mayavi2.standalone
def view():
    from mayavi.modules.surface import Surface
    from simphony_mayavi.sources.api import CUDSSource

    mayavi.new_scene()  # noqa
    src = CUDSSource(cuds=container)
    mayavi.add_source(src)  # noqa
    s = Surface()
    mayavi.add_module(s)  # noqa

if __name__ == '__main__':
    view()
