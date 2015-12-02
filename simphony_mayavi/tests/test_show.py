import unittest

import numpy

from pyface.ui.qt4.util.gui_test_assistant import GuiTestAssistant
from pyface.ui.qt4.util.modal_dialog_tester import ModalDialogTester

from simphony_mayavi.show import show
from simphony.cuds.lattice import make_cubic_lattice
from simphony.cuds.mesh import Mesh, Point
from simphony.cuds.particles import Particles, Particle


class TestShow(unittest.TestCase, GuiTestAssistant):

    def test_lattice_show(self):
        lattice = make_cubic_lattice(
            'test', 0.2, (10, 10, 1), origin=(0.2, -2.4, 0.))

        def function():
            show(lattice)
            return True

        tester = ModalDialogTester(function)
        tester.open_and_run(when_opened=lambda x: x.close(accept=False))
        self.assertTrue(tester.result)

    def test_mesh_show(self):
        points = numpy.array([
            [0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1],
            [2, 0, 0], [3, 0, 0], [3, 1, 0], [2, 1, 0],
            [2, 0, 1], [3, 0, 1], [3, 1, 1], [2, 1, 1]],
            'f')

        mesh = Mesh('test')
        point_iter = (Point(coordinates=point) for point in points)
        mesh.add_points(point_iter)

        def function():
            show(mesh)
            return True

        tester = ModalDialogTester(function)
        tester.open_and_run(when_opened=lambda x: x.close(accept=False))
        self.assertTrue(tester.result)

    def test_particles_snapshot(self):
        coordinates = numpy.array([
            [0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1],
            [2, 0, 0], [3, 0, 0], [3, 1, 0], [2, 1, 0],
            [2, 0, 1], [3, 0, 1], [3, 1, 1], [2, 1, 1]],
            'f')
        particles = Particles('test')
        particle_iter = (Particle(coordinates=point+3)
                         for point in coordinates)
        particles.add_particles(particle_iter)

        def function():
            show(particles)
            return True

        tester = ModalDialogTester(function)
        tester.open_and_run(when_opened=lambda x: x.close(accept=False))
        self.assertTrue(tester.result)

    def test_unknown_container(self):
        container = object()
        with self.assertRaises(TypeError):
            show(container)
