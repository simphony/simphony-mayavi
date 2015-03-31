import unittest


class TestPluginLoading(unittest.TestCase):

    def test_import(self):
        try:
            from simphony.visualisation import mayavi_tools  # noqa
        except ImportError:
            self.fail('Could not import the mayavi visualisation')

    def test_function_api(self):

        from simphony.visualisation import mayavi_tools

        self.assertTrue(hasattr(mayavi_tools, 'show'))
        self.assertTrue(hasattr(mayavi_tools, 'snapshot'))
