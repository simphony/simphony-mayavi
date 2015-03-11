import unittest


class TestPluginLoading(unittest.TestCase):

    def test_import(self):
        try:
            from simphony.visualisation import mayavi_tools
        except ImportError:
            self.fail('Could not import the mayavi visualisation')

        self.assertTrue(hasattr(mayavi_tools, 'show'))
