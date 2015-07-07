import os
import unittest


from simphony_mayavi.load import load
from simphony_mayavi.cuds.api import VTKParticles, VTKMesh


VTKDATA = os.environ.get('VTKDATA', None)


class TestLoad(unittest.TestCase):

    @unittest.skipIf(VTKDATA is None, 'VTKDATA folder not available')
    def setUp(self):
        self.data_folder = os.path.join(VTKDATA, 'Data')

    def test_load_blowGeom_vtk(self):
        # The blowGeom.vtk files contains a mesh surface.
        filename = os.path.join(self.data_folder, 'blowGeom.vtk')
        container = load(filename)
        self.assertIsInstance(container, VTKMesh)
        self.assertEqual(sum(1 for item in container.iter_points()), 687)
        self.assertEqual(sum(1 for item in container.iter_faces()), 1057)
        self.assertEqual(sum(1 for item in container.iter_edges()), 0)
        self.assertEqual(sum(1 for item in container.iter_cells()), 0)

    def test_load_vtk_vtk(self):
        # The vtk.vtk files contains only points and lines
        filename = os.path.join(self.data_folder, 'vtk.vtk')
        container = load(filename)
        self.assertIsInstance(container, VTKParticles)
        self.assertEqual(sum(1 for item in container.iter_particles()), 12)
