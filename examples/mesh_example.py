from numpy import array
from mayavi.scripts import mayavi2

from simphony.cuds.mesh import Mesh, Point, Cell, Edge, Face

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
uids = [
    container.add_point(Point(coordinates=point)) for point in points]

# add edges
edge_uids = [
    container.add_edge(
        Edge(points=[uids[index] for index in element]))
    for element in edges]

# add faces
face_uids = [
    container.add_face(
        Face(points=[uids[index] for index in element]))
    for element in faces]

# add cells
cell_uids = [
    container.add_cell(
        Cell(points=[uids[index] for index in element]))
    for element in cells]


# Now view the data.
@mayavi2.standalone
def view():
    from mayavi.modules.surface import Surface
    from simphony_mayavi.sources.api import MeshSource

    mayavi.new_scene()  # noqa
    src = MeshSource.from_mesh(container)
    mayavi.add_source(src)  # noqa
    s = Surface()
    mayavi.add_module(s)  # noqa

if __name__ == '__main__':
    view()
