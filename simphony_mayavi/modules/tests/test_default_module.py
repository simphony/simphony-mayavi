import unittest

import numpy
from mayavi.modules.api import Surface, Glyph

from simphony.cuds.particles import Particle, Bond, Particles
from simphony.core.data_container import DataContainer
from simphony.cuds.lattice import make_cubic_lattice
from simphony.core.cuba import CUBA
from simphony.cuds.mesh import Mesh, Point, Cell, Edge, Face

from simphony_mayavi.sources.api import CUDSSource
from simphony_mayavi.modules.default_module import default_module


class TestDefaultModule(unittest.TestCase):

    def get_data_names(self, source):
        ''' Return string containing the point/cell's scalar/vector
        names.  For error messages '''

        text = ("point_scalars_name={0}, "
                "point_vectors_name={1}, "
                "cell_scalars_name={2}, "
                "cell_vectors_name={3}")

        return text.format(source.point_scalars_name,
                           source.point_vectors_name,
                           source.cell_scalars_name,
                           source.cell_vectors_name)

    def get_particles(self, has_bond=True):
        ''' Return a Particles dataset with TEMPERATURE, VELOCITY
        and with or without bonds '''

        points = numpy.array([[0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1]], 'f')
        bonds = numpy.array([[0, 1], [0, 3], [1, 3, 2]])
        temperature = numpy.array([10., 20., 30., 40.])
        velocities = numpy.array([[1., 2., 3.],
                                  [0., 1., 2.],
                                  [2., 3., 4.],
                                  [0., -1., -2]])
        particles = Particles('test')

        # add particles
        particle_iter = (Particle(coordinates=point,
                                  data=DataContainer(
                                      TEMPERATURE=temperature[index],
                                      VELOCITY=velocities[index]))
                         for index, point in enumerate(points))
        uids = particles.add(particle_iter)

        if has_bond:
            # add bonds
            bond_iter = (Bond(particles=[uids[index] for index in indices])
                         for indices in bonds)
            particles.add(bond_iter)

        return particles

    def get_lattice(self):
        ''' Return a Lattice dataset with TEMPERATURE as data'''
        lattice = make_cubic_lattice('test', 0.1, (5, 10, 12))

        new_nodes = []
        for node in lattice.iter(item_type=CUBA.NODE):
            index = numpy.array(node.index) + 1.0
            node.data[CUBA.TEMPERATURE] = numpy.prod(index)
            new_nodes.append(node)

        lattice.update(new_nodes)
        return lattice

    def get_mesh(self):
        ''' Return a Mesh dataset with points, cells, faces and
        edges.  Points have VELOCITY and TEMPERATURE as data.
        Cells have VELOCITY and TEMPERATURE as data as well'''
        points = numpy.array([
            [0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1],
            [2, 0, 0], [3, 0, 0], [3, 1, 0], [2, 1, 0],
            [2, 0, 1], [3, 0, 1], [3, 1, 1], [2, 1, 1]],
            'f')

        cells = [[0, 1, 2, 3],  # tetra
                 [4, 5, 6, 7, 8, 9, 10, 11]]  # hex

        faces = [[2, 7, 11]]
        edges = [[1, 4], [3, 8]]

        mesh = Mesh('example')

        # add points
        point_iter = (Point(coordinates=point,
                            data=DataContainer(TEMPERATURE=index,
                                               VELOCITY=(index, 0., 0)))
                      for index, point in enumerate(points))
        uids = mesh.add(point_iter)

        # add edges
        edge_iter = (Edge(points=[uids[index] for index in element])
                     for index, element in enumerate(edges))
        mesh.add(edge_iter)

        # add faces
        face_iter = (Face(points=[uids[index] for index in element])
                     for index, element in enumerate(faces))
        mesh.add(face_iter)

        # add cells
        cell_iter = (Cell(points=[uids[index] for index in element],
                          data=DataContainer(TEMPERATURE=index,
                                             VELOCITY=(index, 0., 0)))
                     for index, element in enumerate(cells))
        mesh.add(cell_iter)
        return mesh

    def test_default_module_particles(self):
        # given
        particles = self.get_particles()
        source = CUDSSource(cuds=particles)

        # when
        # data = TEMPERATURE, VELOCITY, with bonds
        source.point_scalars_name = "TEMPERATURE"
        source.point_vectors_name = "VELOCITY"
        modules = default_module(source)

        # then
        # two Glyph, one Surface
        self.assertEqual(len(modules), 3)
        self.assertEqual(sum((isinstance(module, Glyph)
                              for module in modules)), 2)
        self.assertEqual(sum((isinstance(module, Surface)
                              for module in modules)), 1)

    def test_default_module_particles_with_no_bonds(self):
        # given
        particles = self.get_particles(has_bond=False)
        source = CUDSSource(cuds=particles)

        # when
        # data = TEMPERATURE, VELOCITY, with no bonds
        source.point_scalars_name = "TEMPERATURE"
        source.point_vectors_name = "VELOCITY"
        modules = default_module(source)

        # then
        # modules are two Glyph
        self.assertEqual(len(modules), 2, "There should be 2 modules")
        self.assertTrue(all((isinstance(module, Glyph) for module in modules)),
                        "Not all modules are Glyph")

    def test_default_module_particles_point_scalars_and_bond(self):
        # given
        particles = self.get_particles()
        source = CUDSSource(cuds=particles)

        # when
        # data = TEMPERATURE, with bonds
        source.point_scalars_name = "TEMPERATURE"
        source.point_vectors_name = ""
        modules = default_module(source)
        data_names = self.get_data_names(source)

        # then
        message = "There should be 2 modules for {0} with bonds, got {1}"
        self.assertEqual(len(modules), 2, message.format(data_names, modules))

        message = "Need one of the modules to be a Glyph for {0}, got {1}"
        self.assertEqual(sum((isinstance(module, Glyph)
                              for module in modules)),
                         1,
                         message.format(data_names, modules))

        message = "Need one Surface for particles with bonds, got {}"
        self.assertEqual(sum((isinstance(module, Surface)
                              for module in modules)),
                         1, message.format(modules))

    def test_default_module_particles_point_vectors_only(self):
        # given
        particles = self.get_particles(has_bond=False)
        source = CUDSSource(cuds=particles)

        # when
        # data = TEMPERATURE, with bonds
        source.point_scalars_name = ""
        source.point_vectors_name = "VELOCITY"
        modules = default_module(source)

        # then
        self.assertEqual(len(modules), 1)
        self.assertIsInstance(modules[0], Glyph)

    def test_default_module_lattice(self):
        # given
        lattice = self.get_lattice()

        # when
        # just point scalars
        modules = default_module(CUDSSource(cuds=lattice))

        # then
        # module is a Glyph
        self.assertEqual(len(modules), 1)
        self.assertIsInstance(modules[0], Glyph)

    def test_default_module_mesh(self):
        # given
        mesh = self.get_mesh()
        source = CUDSSource(cuds=mesh)

        # when
        modules = default_module(source)
        data_names = self.get_data_names(source)

        # then
        # two Glyphs, two Surface
        self.assertEqual(len(modules), 4)
        message = "Need 2 of the modules to be Glyph for {0}, got {1}"
        self.assertEqual(sum((isinstance(module, Glyph)
                              for module in modules)),
                         2, message.format(data_names, modules))
        message = "Need 2 of the modules to be Surface for {0}, got {1}"
        self.assertEqual(sum((isinstance(module, Surface)
                              for module in modules)),
                         2, message.format(data_names, modules))

    def test_default_module_empty_data(self):
        # given
        lattice = make_cubic_lattice("test", 0.2, (10, 10, 1))
        source = CUDSSource(cuds=lattice)

        # when
        modules = default_module(source)

        # then
        # one Glyph as default when no data is found
        self.assertEqual(len(modules), 1)
        self.assertIsInstance(modules[0], Glyph)
