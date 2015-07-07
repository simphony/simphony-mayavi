import unittest

PLUGINAPI = [
    'show',
    'snapshot',
    'VTKParticles',
    'VTKLattice',
    'VTKMesh',
    'adapt2cuds',
    'load']


class TestPluginLoading(unittest.TestCase):

    def test_import(self):
        try:
            from simphony.visualisation import mayavi_tools  # noqa
        except ImportError:
            self.fail('Could not import the mayavi visualisation')

    def test_function_api(self):

        from simphony.visualisation import mayavi_tools

        for item in PLUGINAPI:
            self.assertTrue(
                hasattr(mayavi_tools, item),
                "could not import {}".format(item))
