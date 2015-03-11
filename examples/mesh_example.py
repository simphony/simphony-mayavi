from numpy import array
from mayavi.scripts import mayavi2

from simphony.cuds.mesh import Mesh, Point, Cell

points = array([
    [0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1],
    [2, 0, 0], [3, 0, 0], [3, 1, 0], [2, 1, 0],
    [2, 0, 1], [3, 0, 1], [3, 1, 1], [2, 1, 1]],
    'f')

cells = array([
    4, 0, 1, 2, 3,  # tetra
    8, 4, 5, 6, 7, 8, 9, 10, 11  # hex
])

container = Mesh('test')
uids = [
    container.add_point(Point(coordinates=point)) for point in points]
container.add_cell(Cell(points=[uids[index] for index in cells[:5]]))
container.add_cell(Cell(points=[uids[index] for index in cells[5:]]))


# Now view the data.
@mayavi2.standalone
def view():
    from mayavi.modules.surface import Surface
    from simphony.visualization import mayavi_tools as tools

    mayavi.new_scene()  # noqa
    src = tools.MeshSource.from_particles(container)
    mayavi.add_source(src)  # noqa
    s = Surface()
    mayavi.add_module(s)  # noqa

if __name__ == '__main__':
    view()
