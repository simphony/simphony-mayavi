import unittest


class TestPluginLoading(unittest.TestCase):

    def test_import(self):
        try:
            from simphony.visualization import mayavi_tools
        except ImportError:
            self.fail('Could not import the mayavi visualization')

        self.assertTrue(hasattr(mayavi_tools, 'show'))
