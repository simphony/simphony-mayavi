import unittest
from mock import patch, Mock, sentinel

from simphony_mayavi.plugins.engine_wrappers.openfoam import ENGINE_REGISTRY


class TestOpenFoam(unittest.TestCase):
    def setUp(self):
        self.mock_Wrapper = Mock(return_value=sentinel.wrapper_out)
        self.mock_FoamControlWrapper = Mock(
            return_value=sentinel.foam_control_wrapper_out)
        self.mock_FoamInternalWrapper = Mock(
            return_value=sentinel.foam_internal_wrapper_out)

    def test_openfoam_file_io_factory(self):
        with patch("simphony.engine.openfoam_file_io", create=True) as p:
            p.Wrapper = self.mock_Wrapper
            engine_factory = ENGINE_REGISTRY["openfoam_file_io"]
            self.assertEqual(engine_factory.create(), sentinel.wrapper_out)
            del p.Wrapper
            p.FoamControlWrapper = self.mock_FoamControlWrapper
            self.assertEqual(
                engine_factory.create(),
                sentinel.foam_control_wrapper_out
                )

    def test_openfoam_internal_factory(self):
        with patch("simphony.engine.openfoam_internal", create=True) as p:
            p.Wrapper = self.mock_Wrapper
            engine_factory = ENGINE_REGISTRY["openfoam_internal"]
            self.assertEqual(engine_factory.create(), sentinel.wrapper_out)
            del p.Wrapper
            p.FoamInternalWrapper = self.mock_FoamInternalWrapper
            self.assertEqual(
                engine_factory.create(),
                sentinel.foam_internal_wrapper_out
                )
