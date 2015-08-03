from contextlib import closing

from mayavi.scripts import mayavi2
import numpy
from numpy import array
from simphony.core.data_container import DataContainer
from simphony.core.cuba import CUBA
from simphony.cuds.particles import Particles, Particle, Bond
from simphony.cuds.lattice import (
    make_hexagonal_lattice, make_cubic_lattice, make_square_lattice)
from simphony.cuds.mesh import Mesh, Point, Cell, Edge, Face
from simphony.io.h5_cuds import H5CUDS

points = array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]], 'f')
bonds = array([[0, 1], [0, 3], [1, 3, 2]])
temperature = array([10., 20., 30., 40.])

particles = Particles('particles_example')
uids = []
for index, point in enumerate(points):
    uid = particles.add_particle(
        Particle(
            coordinates=point,
            data=DataContainer(TEMPERATURE=temperature[index])))
    uids.append(uid)
for indices in bonds:
    particles.add_bond(Bond(particles=[uids[index] for index in indices]))

hexagonal = make_hexagonal_lattice('hexagonal', 0.1, (5, 4))
square = make_square_lattice('square', 0.1, (5, 4))
cubic = make_cubic_lattice('cubic', 0.1, (5, 10, 12))


def add_temperature(lattice):
    for node in lattice.iter_nodes():
        index = numpy.array(node.index) + 1.0
        node.data[CUBA.TEMPERATURE] = numpy.prod(index)
        lattice.update_node(node)


def add_velocity(lattice):
    for node in lattice.iter_nodes():
        node.data[CUBA.VELOCITY] = node.index
        lattice.update_node(node)

add_temperature(hexagonal)
add_temperature(cubic)
add_temperature(square)
add_velocity(hexagonal)
add_velocity(cubic)
add_velocity(square)

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
uids = [
    mesh.add_point(
        Point(coordinates=point, data=DataContainer(TEMPERATURE=index)))
    for index, point in enumerate(points)]

# add edges
edge_uids = [
    mesh.add_edge(
        Edge(
            points=[uids[index] for index in element],
            data=DataContainer(TEMPERATURE=index + 20)))
    for index, element in enumerate(edges)]

# add faces
face_uids = [
    mesh.add_face(
        Face(
            points=[uids[index] for index in element],
            data=DataContainer(TEMPERATURE=index + 30)))
    for index, element in enumerate(faces)]

# add cells
cell_uids = [
    mesh.add_cell(
        Cell(
            points=[uids[index] for index in element],
            data=DataContainer(TEMPERATURE=index + 40)))
    for index, element in enumerate(cells)]


# save the data into cuds.
with closing(H5CUDS.open('example.cuds', 'w')) as handle:
    handle.add_mesh(mesh)
    handle.add_particles(particles)
    handle.add_lattice(hexagonal)
    handle.add_lattice(cubic)
    handle.add_lattice(square)


# Now view the data.
@mayavi2.standalone
def view():
    mayavi.new_scene()  # noqa

if __name__ == '__main__':
    view()
