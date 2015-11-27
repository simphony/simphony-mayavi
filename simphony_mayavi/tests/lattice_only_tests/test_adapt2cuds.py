import unittest

from hypothesis import given
from hypothesis.strategies import sampled_from

from simphony.core.cuba import CUBA
from simphony.cuds.abc_lattice import ABCLattice
from simphony_mayavi.api import adapt2cuds

from simphony_mayavi.tests.test_adapt2cuds import (create_image_data,
                                                   create_poly_data)

good_data_sets = sampled_from([
    (create_image_data(array_name='TEMPERATURE'), 'lattice'),
    (create_poly_data(array_name='TEMPERATURE'), 'lattice')])

bad_array_data_sets = sampled_from([
    (create_image_data(), 'lattice'),
    (create_poly_data(), 'lattice')])

auto_data_sets = sampled_from([
    (create_image_data(array_name='TEMPERATURE'), 'lattice'),
    (create_poly_data(array_name='TEMPERATURE'), 'lattice')])

expected = {'lattice': ABCLattice}


class TestAdapt2Cuds(unittest.TestCase):

    @given(good_data_sets)
    def test_adapt_data_set(self, setup):
        data_set, kind = setup
        container = adapt2cuds(data_set, 'test', kind)
        self.assertIsInstance(container, expected[kind])
        self.assertIs(container.data_set, data_set)

    @given(bad_array_data_sets)
    def test_adapt_data_set_with_array_rename(self, setup):
        data_set, kind = setup
        container = adapt2cuds(
            data_set, 'test', kind,
            rename_arrays={'scalars': CUBA.TEMPERATURE})
        self.assertIsInstance(container, expected[kind])
        self.assertIsNot(container.data_set, data_set)

    @given(auto_data_sets)
    def test_adapt_data_set_with_auto_detect(self, setup):
        data_set, kind = setup
        container = adapt2cuds(data_set, 'test')
        self.assertIsInstance(container, expected[kind])
        self.assertIs(container.data_set, data_set)
