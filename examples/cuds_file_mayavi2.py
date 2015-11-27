from contextlib import closing

from mayavi.scripts import mayavi2
import numpy
from numpy import array
from simphony.core.data_container import DataContainer
from simphony.core.cuba import CUBA
from simphony.cuds.particles import Particles, Particle, Bond
from simphony.cuds.lattice import (
    make_hexagonal_lattice, make_orthorhombic_lattice,
    make_body_centered_orthorhombic_lattice)
from simphony.cuds.mesh import Mesh, Point, Cell, Edge, Face
from simphony.io.h5_cuds import H5CUDS

points = array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]], 'f')
bonds = array([[0, 1], [0, 3], [1, 3, 2]])
temperature = array([10., 20., 30., 40.])

# particles container
particles = Particles('particles_example')

# add particles
particle_iter = (Particle(coordinates=point,
                          data=DataContainer(TEMPERATURE=temperature[index]))
                 for index, point in enumerate(points))
uids = particles.add_particles(particle_iter)

# add bonds
bond_iter = (Bond(particles=[uids[index] for index in indices])
             for indices in bonds)
particles.add_bonds(bond_iter)


hexagonal = make_hexagonal_lattice(
    'hexagonal', 0.1, 0.1, (5, 5, 5), (5, 4, 0))
orthorhombic = make_orthorhombic_lattice(
    'orthorhombic', (0.1, 0.2, 0.3), (5, 5, 5), (5, 4, 0))
body_centered = make_body_centered_orthorhombic_lattice(
    'body_centered', (0.1, 0.2, 0.3), (5, 5, 5), (5, 10, 12))


def add_temperature(lattice):
    new_nodes = []
    for node in lattice.iter_nodes():
        index = numpy.array(node.index) + 1.0
        node.data[CUBA.TEMPERATURE] = numpy.prod(index)
        new_nodes.append(node)
    lattice.update_nodes(new_nodes)


def add_velocity(lattice):
    new_nodes = []
    for node in lattice.iter_nodes():
        node.data[CUBA.VELOCITY] = node.index
        new_nodes.append(node)
    lattice.update_nodes(new_nodes)

add_temperature(hexagonal)
add_temperature(orthorhombic)
add_temperature(body_centered)
add_velocity(hexagonal)
add_velocity(orthorhombic)
add_velocity(body_centered)

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

mesh = Mesh('mesh_example')

# add points
uids = mesh.add_points((Point(coordinates=point,
                              data=DataContainer(TEMPERATURE=index))
                        for index, point in enumerate(points)))

# add edges
edge_iter = (Edge(points=[uids[index] for index in element],
                  data=DataContainer(TEMPERATURE=index + 20))
             for index, element in enumerate(edges))
edge_uids = mesh.add_edges(edge_iter)

# add faces
face_uids = mesh.add_faces((Face(points=[uids[index] for index in element],
                                 data=DataContainer(TEMPERATURE=index + 30))
                            for index, element in enumerate(faces)))

# add cells
cell_uids = mesh.add_cells((Cell(points=[uids[index] for index in element],
                                 data=DataContainer(TEMPERATURE=index + 40))
                            for index, element in enumerate(cells)))


# save the data into cuds.
with closing(H5CUDS.open('example.cuds', 'w')) as handle:
    handle.add_dataset(mesh)
    handle.add_dataset(particles)
    handle.add_dataset(hexagonal)
    handle.add_dataset(orthorhombic)
    handle.add_dataset(body_centered)


# Now view the data.
@mayavi2.standalone
def view():
    mayavi.new_scene()  # noqa

if __name__ == '__main__':
    view()
