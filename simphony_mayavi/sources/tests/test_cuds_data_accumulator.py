import unittest

from numpy.testing import assert_array_equal
from simphony.core.cuba import CUBA
from simphony.testing.utils import create_data_container, dummy_cuba_value

from simphony_mayavi.sources.cuds_data_accumulator import CUDSDataAccumulator


class TestCUDSDataAccumulator(unittest.TestCase):

    def test_accumulate(self):

        cuds_data = [create_data_container() for i in range(10)]
        accumulator = CUDSDataAccumulator()
        for data in cuds_data:
            accumulator.append(data)

        self.assertEqual(len(accumulator), 10)
        self.assertEqual(accumulator.keys, set(CUBA))
        for cuba in CUBA:
            assert_array_equal(
                accumulator[cuba], [dummy_cuba_value(cuba)] * 10)

    def test_accumulate_on_keys(self):

        cuds_data = [create_data_container() for i in range(10)]
        accumulator = CUDSDataAccumulator(keys=[CUBA.NAME, CUBA.TEMPERATURE])
        for data in cuds_data:
            accumulator.append(data)

        self.assertEqual(len(accumulator), 10)
        self.assertEqual(accumulator.keys, set([CUBA.NAME, CUBA.TEMPERATURE]))
        for cuba in [CUBA.NAME, CUBA.TEMPERATURE]:
            assert_array_equal(
                accumulator[cuba], [dummy_cuba_value(cuba)] * 10)

    def test_accumulate_with_missing_values(self):

        accumulator = CUDSDataAccumulator()
        accumulator.append(create_data_container())
        accumulator.append(
            create_data_container(restrict=[CUBA.NAME, CUBA.TEMPERATURE]))

        self.assertEqual(len(accumulator), 2)
        self.assertEqual(accumulator.keys, set(CUBA))
        for cuba in CUBA:
            if cuba in [CUBA.NAME, CUBA.TEMPERATURE]:
                assert_array_equal(
                    accumulator[cuba], [dummy_cuba_value(cuba)] * 2)
            else:
                assert_array_equal(
                    accumulator[cuba][0], dummy_cuba_value(cuba))
                self.assertIsNone(accumulator[cuba][1])

    def test_accumulate_and_expand(self):

        accumulator = CUDSDataAccumulator()
        accumulator.append(create_data_container(restrict=[CUBA.NAME]))
        accumulator.append(
            create_data_container(restrict=[CUBA.NAME, CUBA.TEMPERATURE]))

        self.assertEqual(len(accumulator), 2)
        self.assertEqual(accumulator.keys, set([CUBA.NAME, CUBA.TEMPERATURE]))
        assert_array_equal(
            accumulator[CUBA.TEMPERATURE],
            [None, dummy_cuba_value(CUBA.TEMPERATURE)])
        assert_array_equal(
            accumulator[CUBA.NAME],
            [dummy_cuba_value(CUBA.NAME)] * 2)
