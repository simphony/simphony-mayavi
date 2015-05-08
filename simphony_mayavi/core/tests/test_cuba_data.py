import unittest
from functools import partial


import numpy
from tvtk.api import tvtk
from simphony.core.cuba import CUBA
from simphony.core.data_container import DataContainer
from simphony.core.keywords import KEYWORDS
from simphony.testing.utils import compare_data_containers

from simphony_mayavi.core.cuba_data import CubaData, AttributeSetType, MASKED


class TestCubaData(unittest.TestCase):

    def setUp(self):
        self.addTypeEqualityFunc(
            DataContainer, partial(compare_data_containers, testcase=self))
        self.values = {
            'TEMPERATURE': [1.0, 2.0, 3.0],
            'RADIUS': [4.0, 2.0, 1.0],
            'VELOCITY': [[4.0, 2.0, 1.0], [3.0, 2.0, 5.0], [4.0, 5.0, 1.0]]}
        self.point_data = point_data = tvtk.PointData()
        for key in self.values:
            index = point_data.add_array(self.values[key])
            point_data.get_array(index).name = key
            index = point_data.add_array(
                numpy.ones(shape=(len(self.values[key]),), dtype=numpy.uint8))
            point_data.get_array(index).name = MASKED.format(key)
        self.data = CubaData(attribute_data=point_data)

    def test_len(self):
        # given
        point_data = tvtk.PointData()
        data = CubaData(attribute_data=point_data)

        # then
        self.assertEqual(len(data), 0)

        # when
        point_data.add_array([0, 0, 0, 3])

        # then
        self.assertEqual(len(data), 4)

    def test_initialize_empty_points(self):
        # given
        data = CubaData.empty()

        # then
        self.assertEqual(len(data), 0)
        self.assertEqual(data.cubas, set([]))
        self.assertIsInstance(data._data, tvtk.PointData)

    def test_initialize_empty_cells(self):
        # given
        data = CubaData.empty(AttributeSetType.CELLS)

        # then
        self.assertEqual(len(data), 0)
        self.assertEqual(data.cubas, set([]))
        self.assertIsInstance(data._data, tvtk.CellData)

    def test_initialize_with_point_data(self):
        # given
        point_data = tvtk.PointData()
        index = point_data.add_array([1, 2, 3])
        point_data.get_array(index).name = CUBA.TEMPERATURE.name
        index = point_data.add_array(numpy.array([1, 1, 1], dtype=numpy.uint8))
        point_data.get_array(index).name = MASKED.format(CUBA.TEMPERATURE.name)
        index = point_data.add_array([4, 2, 1])
        point_data.get_array(index).name = CUBA.RADIUS.name
        index = point_data.add_array(numpy.array([1, 1, 1], dtype=numpy.uint8))
        point_data.get_array(index).name = MASKED.format(CUBA.RADIUS.name)

        # when
        data = CubaData(attribute_data=point_data)

        # then
        self.assertEqual(data.cubas, {CUBA.TEMPERATURE, CUBA.RADIUS})

    def test_getitem(self):
        # given
        data = self.data
        values = self.values

        # when/then
        for index in range(3):
            result = data[index]
            expected = DataContainer(
                RADIUS=values['RADIUS'][index],
                TEMPERATURE=values['TEMPERATURE'][index],
                VELOCITY=values['VELOCITY'][index])
            self.assertEqual(result, expected)

        # when/then
        with self.assertRaises(IndexError):
            data[4]

    def test_getitem_with_long_int_index(self):
        # given
        data = self.data
        values = self.values

        # when/then
        for index in range(3):
            result = data[long(index)]
            expected = DataContainer(
                RADIUS=values['RADIUS'][index],
                TEMPERATURE=values['TEMPERATURE'][index],
                VELOCITY=values['VELOCITY'][index])
            self.assertEqual(result, expected)

        # when/then
        with self.assertRaises(IndexError):
            data[long(4)]

    def test_getitem_with_integer_values(self):
        # given
        data = self.data
        values = self.values
        point_data = self.point_data
        # We need to get a CUBA key that has an int value.
        INTEGER_CUBA_KEY = next(
            key for key in KEYWORDS if KEYWORDS[key].dtype == numpy.int32)
        array_id = point_data.add_array([1, 0, 1])
        point_data.get_array(array_id).name = INTEGER_CUBA_KEY
        array_id = point_data.add_array(
            numpy.array([1, 1, 1], dtype=numpy.uint8))
        point_data.get_array(array_id).name = MASKED.format(INTEGER_CUBA_KEY)

        # when/then
        for index in range(3):
            result = data[long(index)]
            expected = DataContainer(
                RADIUS=values['RADIUS'][index],
                TEMPERATURE=values['TEMPERATURE'][index],
                VELOCITY=values['VELOCITY'][index])
            expected[CUBA[INTEGER_CUBA_KEY]] = [1, 0, 1][index]
            self.assertEqual(result, expected)

        # when/then
        with self.assertRaises(IndexError):
            data[long(4)]

    def test_setitem(self):
        # given
        data = self.data

        # when
        for index in range(3):
            data[index] = DataContainer(
                RADIUS=[34, 32, 31][index],
                TEMPERATURE=[-1, -2, -3][index],
                VELOCITY=[0.2, -0.1, -0.54])

        # then
        for index in range(3):
            self.assertEqual(
                data[index], DataContainer(
                    RADIUS=[34, 32, 31][index],
                    TEMPERATURE=[-1, -2, -3][index],
                    VELOCITY=[0.2, -0.1, -0.54]))
        self._assert_len(data, 3)

        # when/then
        with self.assertRaises(IndexError):
            data[4] = DataContainer(RADIUS=0.2, TEMPERATURE=-4.5)

    def test_setitem_with_unsupported_cuba(self):
        # given
        data = self.data

        # when
        for index in range(3):
            data[index] = DataContainer(
                RADIUS=[34, 32, 31][index],
                TEMPERATURE=[-1, -2, -3][index],
                VELOCITY=[0.2, -0.1, -0.54],
                NAME=str(index))

        # then
        for index in range(3):
            self.assertEqual(
                data[index], DataContainer(
                    RADIUS=[34, 32, 31][index],
                    TEMPERATURE=[-1, -2, -3][index],
                    VELOCITY=[0.2, -0.1, -0.54]))
        self._assert_len(data, 3)

        # when/then
        with self.assertRaises(IndexError):
            data[4] = DataContainer(RADIUS=0.2, TEMPERATURE=-4.5)

    def test_setitem_with_long_int(self):
        # given
        data = self.data

        # when
        for index in range(3):
            data[long(index)] = DataContainer(
                RADIUS=[34, 32, 31][index],
                TEMPERATURE=[-1, -2, -3][index],
                VELOCITY=[0.2, -0.1, -0.54])

        # then
        for index in range(3):
            self.assertEqual(
                data[index], DataContainer(
                    RADIUS=[34, 32, 31][index],
                    TEMPERATURE=[-1, -2, -3][index],
                    VELOCITY=[0.2, -0.1, -0.54]))
        self._assert_len(data, 3)

        # when/then
        with self.assertRaises(IndexError):
            data[4] = DataContainer(RADIUS=0.2, TEMPERATURE=-4.5)

    def test_setitem_with_new_scalar_cubas(self):
        # given
        data = self.data

        # when
        for index in range(3):
            data[index] = DataContainer(
                RADIUS=[34, 32, 31][index], TEMPERATURE=[-1, -2, -3][index],
                MASS=[0.1, 0.4, 0.3][index], VELOCITY=[0.2, -0.1, -0.54])

        # then
        for index in range(3):
            self.assertEqual(
                data[index], DataContainer(
                    RADIUS=[34, 32, 31][index],
                    TEMPERATURE=[-1, -2, -3][index],
                    MASS=[0.1, 0.4, 0.3][index],
                    VELOCITY=[0.2, -0.1, -0.54]))
        self._assert_len(data, 3)

    def test_setitem_with_new_vector_cubas(self):
        # given
        data = self.data

        # when
        for index in range(3):
            data[index] = DataContainer(
                RADIUS=[34, 32, 31][index], TEMPERATURE=[-1, -2, -3][index],
                DIRECTION=[1, 4, 3], VELOCITY=[0.1, 0.4, 0.3])

        # then
        for index in range(3):
            self.assertEqual(
                data[index], DataContainer(
                    RADIUS=[34, 32, 31][index],
                    TEMPERATURE=[-1, -2, -3][index],
                    VELOCITY=[0.1, 0.4, 0.3],
                    DIRECTION=[1, 4, 3]))

    def test_setitem_with_missing_scalar_cubas(self):
        # given
        data = self.data

        # when
        for index in range(3):
            data[index] = DataContainer(
                TEMPERATURE=[-1, -2, -3][index], VELOCITY=[0.1, 0.4, 0.3])

        # then
        for index in range(3):
            self.assertEqual(
                data[index], DataContainer(
                    TEMPERATURE=[-1, -2, -3][index],
                    VELOCITY=[0.1, 0.4, 0.3]))
        self._assert_len(data, 3)

    def test_setitem_with_missing_vector_cubas(self):
        # given
        data = self.data

        # when
        for index in range(3):
            data[index] = DataContainer(
                TEMPERATURE=[-1, -2, -3][index],
                RADIUS=[0.12, -33, 11][index])

        # then
        for index in range(3):
            self.assertEqual(
                data[index], DataContainer(
                    RADIUS=[0.12, -33, 11][index],
                    TEMPERATURE=[-1, -2, -3][index]))
        self._assert_len(data, 3)

    def test_setitem_with_invalid_index(self):
        # given
        data = self.data

        # when
        with self.assertRaises(IndexError):
            data[5] = DataContainer(MASS=45)

        # then
        self.assertEqual(len(data), 3)
        self.assertNotIn(CUBA.MASS, data[0])
        self._assert_len(data, 3)

    def test_delitem(self):
        # given
        data = self.data
        values = self.values

        # when
        del data[1]

        # the
        self.assertEqual(len(data), 2)
        for new_index, old_index in enumerate((0, 2)):
            result = data[new_index]
            self.assertEqual(
                result, DataContainer(
                    RADIUS=values['RADIUS'][old_index],
                    TEMPERATURE=values['TEMPERATURE'][old_index],
                    VELOCITY=values['VELOCITY'][old_index]))
        self._assert_len(data, 2)

    def test_append(self):
        # given
        data = self.data
        values = self.values

        # when
        data.append(DataContainer(VELOCITY=[0, 0, 0.34]))

        # then
        self.assertEqual(len(data), 4)
        for index in range(3):
            result = data[index]
            self.assertEqual(
                result, DataContainer(
                    RADIUS=values['RADIUS'][index],
                    TEMPERATURE=values['TEMPERATURE'][index],
                    VELOCITY=values['VELOCITY'][index]))
        self.assertEqual(data[3], DataContainer(VELOCITY=[0, 0, 0.34]))
        self._assert_len(data, 4)

    def test_append_with_new_cuba(self):
        # given
        data = self.data
        values = self.values

        # when
        data.append(DataContainer(MASS=34, VELOCITY=[0, 0, 0.34]))

        # then
        self.assertEqual(len(data), 4)
        for index in range(3):
            result = data[index]
            self.assertEqual(
                result, DataContainer(
                    RADIUS=values['RADIUS'][index],
                    TEMPERATURE=values['TEMPERATURE'][index],
                    VELOCITY=values['VELOCITY'][index]))
        self.assertEqual(
            data[3], DataContainer(MASS=34.0, VELOCITY=[0, 0, 0.34]))

    def test_append_with_unsupported_cuba(self):
        # given
        data = self.data
        values = self.values

        # when
        data.append(DataContainer(VELOCITY=[0, 0, 0.34], NAME='my name'))

        # then
        self.assertEqual(len(data), 4)
        for index in range(3):
            result = data[index]
            self.assertEqual(
                result, DataContainer(
                    RADIUS=values['RADIUS'][index],
                    TEMPERATURE=values['TEMPERATURE'][index],
                    VELOCITY=values['VELOCITY'][index]))
        self.assertEqual(data[3], DataContainer(VELOCITY=[0, 0, 0.34]))
        self._assert_len(data, 4)

    def test_insert(self):
        # given
        data = self.data
        values = self.values

        # when
        data.insert(1, DataContainer(VELOCITY=[0, 0, 0.34]))
        self._assert_len(data, 4)

        # then
        self.assertEqual(len(data), 4)
        for old_index, index in enumerate((0, 2, 3)):
            result = data[index]
            self.assertEqual(
                result, DataContainer(
                    RADIUS=values['RADIUS'][old_index],
                    TEMPERATURE=values['TEMPERATURE'][old_index],
                    VELOCITY=values['VELOCITY'][old_index]))
        self.assertEqual(data[1], DataContainer(VELOCITY=[0, 0, 0.34]))

    def test_insert_with_new_cuba(self):
        # given
        data = self.data
        values = self.values

        # when
        data.insert(1, DataContainer(VELOCITY=[0, 0, 0.34], MASS=0.3))
        self._assert_len(data, 4)

        # then
        self.assertEqual(len(data), 4)
        for old_index, index in enumerate((0, 2, 3)):
            result = data[index]
            self.assertEqual(
                result, DataContainer(
                    RADIUS=values['RADIUS'][old_index],
                    TEMPERATURE=values['TEMPERATURE'][old_index],
                    VELOCITY=values['VELOCITY'][old_index]))
        self.assertEqual(
            data[1], DataContainer(VELOCITY=[0, 0, 0.34], MASS=0.3))

    def test_insert_with_unsupported_cuba(self):
        # given
        data = self.data
        values = self.values

        # when
        data.insert(1, DataContainer(VELOCITY=[0, 0, 0.34], NAME='my name2'))
        self._assert_len(data, 4)

        # then
        self.assertEqual(len(data), 4)
        for old_index, index in enumerate((0, 2, 3)):
            result = data[index]
            self.assertEqual(
                result, DataContainer(
                    RADIUS=values['RADIUS'][old_index],
                    TEMPERATURE=values['TEMPERATURE'][old_index],
                    VELOCITY=values['VELOCITY'][old_index]))
        self.assertEqual(data[1], DataContainer(VELOCITY=[0, 0, 0.34]))

    def _assert_len(self, data, length):
        n = data._data.number_of_arrays
        for array_id in range(n):
            self.assertEqual(len(data._data.get_array(array_id)), length)
