import unittest
from collections import Iterable

from simphony_mayavi.tests.testing_utils import DummyEngine
from simphony_mayavi.plugins.tabbed_panel_collection import (
    TabbedPanelCollection)
from simphony_mayavi.sources.api import EngineSource


class TestTabbedPannelCollection(unittest.TestCase):
    def setUp(self):
        engine1 = DummyEngine()
        self.tab1 = EngineSource(engine=engine1)

        engine2 = DummyEngine()
        self.tab2 = EngineSource(engine=engine2)

        self.tabs = TabbedPanelCollection.create(tab1=self.tab1,
                                                 tab2=self.tab2)

    def test_attributes(self):
        self.assertEqual(self.tabs.tab1, self.tab1)
        self.assertEqual(self.tabs.tab2, self.tab2)

    def test_iterable(self):
        self.assertIsInstance(self.tabs, Iterable)

    def test_configure_traits(self):
        ui = self.tabs.edit_traits()
        ui.dispose()

    def test_error_init_predefined_attributes(self):
        with self.assertRaises(AttributeError):
            TabbedPanelCollection.create(get=self.tab1)
