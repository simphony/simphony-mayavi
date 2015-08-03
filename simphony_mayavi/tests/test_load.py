import os
import unittest


from simphony.core.cuba import CUBA
from simphony_mayavi.load import load
from simphony_mayavi.cuds.api import VTKParticles, VTKMesh, VTKLattice


VTKDATA = os.environ.get('VTKDATA')


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

    def test_load_vase_1comp_vti(self):
        # The vase_1comp_vti files contains only points.
        filename = os.path.join(self.data_folder, 'vase_1comp.vti')
        container = load(
            filename, rename_arrays={'SLCImage': CUBA.TEMPERATURE})
        self.assertIsInstance(container, VTKLattice)

    def test_load_vwgt_graph(self):
        # The vwgt.graph file do not have a predefined reader.
        filename = os.path.join(self.data_folder, 'vwgt.graph')

        with self.assertRaises(RuntimeError) as context:
            load(filename)
        message = context.exception.message
        self.assertIn('No suitable reader found', message)