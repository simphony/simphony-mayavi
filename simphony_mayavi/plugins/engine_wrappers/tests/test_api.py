import unittest
from mock import patch

from simphony_mayavi.plugins.engine_wrappers.abc_engine_factory import (
    ABCEngineFactory)


class TestDefaultEngineFactoryAPI(unittest.TestCase):

    @patch("simphony_mayavi.plugins.engine_wrappers.loaded_engines.LOADED_ENGINES",  # noqa
           ("kratos", "jyulb_fileio_isothermal"))
    def test_default_engine_factories(self):

        from simphony_mayavi.plugins.engine_wrappers.api import (
            DEFAULT_ENGINE_FACTORIES)

        self.assertEqual(len(DEFAULT_ENGINE_FACTORIES), 2)
        self.assertIn("kratos", DEFAULT_ENGINE_FACTORIES)
        self.assertIn("jyulb_fileio_isothermal", DEFAULT_ENGINE_FACTORIES)
        for factory in DEFAULT_ENGINE_FACTORIES.values():
            self.assertIsInstance(factory, ABCEngineFactory)
