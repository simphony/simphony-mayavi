import unittest

from .test_adapt2cuds import TestAdapt2Cuds
from simphony_mayavi.tests.test_load import TestLoad
from simphony_mayavi.tests.test_plugin_loading import TestPluginLoading
from simphony_mayavi.tests.test_show import TestShow
from simphony_mayavi.tests.test_snapshot import TestSnapShot
from simphony_mayavi.cuds.tests.test_vtk_lattice import (
    TestVTKLatticeNodeOperations, TestVTKLatticeNodeCoordinates,
    TestVTKLattice)

def load_tests(loader, tests, pattern):
    # customised to remove particle and mesh
    suite = unittest.TestSuite([
            unittest.TestLoader().loadTestsFromTestCase(TestAdapt2Cuds),
            unittest.TestLoader().loadTestsFromTestCase(TestVTKLatticeNodeOperations),
            unittest.TestLoader().loadTestsFromTestCase(TestVTKLatticeNodeCoordinates),
            unittest.TestLoader().loadTestsFromTestCase(TestVTKLattice)])

    suite.addTest(TestLoad("test_load_vase_1comp_vti"))
    suite.addTest(TestPluginLoading("test_import"))
    suite.addTest(TestPluginLoading("test_function_api"))
    suite.addTest(TestShow("test_lattice_show"))
    suite.addTest(TestSnapShot("test_lattice_snapshot"))
    return suite
