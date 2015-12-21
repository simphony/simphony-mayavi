import unittest

import numpy
from numpy.testing import assert_array_almost_equal
from simphony.core.keywords import KEYWORDS
from simphony.core.cuba import CUBA

from simphony_mayavi.core.cuba_utils import (
    supported_cuba, default_cuba_value, empty_array)


class TestCubaUtils(unittest.TestCase):

    def setUp(self):
        self.float_scalar_cuba = [
            cuba for cuba in CUBA
            if KEYWORDS[cuba.name].shape == [1] and numpy.issubdtype(
                KEYWORDS[cuba.name].dtype, numpy.float)]
        self.int_scalar_cuba = [
            cuba for cuba in CUBA
            if KEYWORDS[cuba.name].shape == [1] and numpy.issubdtype(
                KEYWORDS[cuba.name].dtype, numpy.int)]
        self.float_vector_cuba = [
            cuba for cuba in CUBA
            if KEYWORDS[cuba.name].shape == [3] and numpy.issubdtype(
                KEYWORDS[cuba.name].dtype, numpy.float)]
        self.int_vector_cuba = [
            cuba for cuba in CUBA
            if KEYWORDS[cuba.name].shape == [3] and numpy.issubdtype(
                KEYWORDS[cuba.name].dtype, numpy.int)]

    def test_supported_cuba(self):
        # given
        expected = (
            self.float_scalar_cuba + self.int_scalar_cuba +
            self.float_vector_cuba + self.int_vector_cuba)

        # when
        supported = supported_cuba()

        # then
        self.assertItemsEqual(supported, expected)

    def test_default_cuba_value(self):
        for cuba in self.float_scalar_cuba:
            self.assertTrue(numpy.isnan(default_cuba_value(cuba)))
        for cuba in self.int_scalar_cuba:
            self.assertEqual(default_cuba_value(cuba), -1)
        for cuba in self.float_vector_cuba:
            default = default_cuba_value(cuba)
            for value in default:
                self.assertTrue(
                    all(numpy.isnan(default_cuba_value(cuba))))
        for cuba in self.int_vector_cuba:
            self.assertTrue(numpy.isnan(default_cuba_value(cuba)))

    def test_empty_scalar_array(self):
        # when
        empty = empty_array(CUBA.RADIUS, 23)

        # then
        self.assertEqual(empty.shape, (23, 1))
        for index in range(23):
            self.assertTrue(numpy.isnan(empty[index]))

    def test_empty_vector_array(self):
        # when
        empty = empty_array(CUBA.VELOCITY, 23)

        # then
        self.assertEqual(empty.shape, (23, 3))
        for index in range(23):
            for column in range(3):
                self.assertTrue(numpy.isnan(empty[index, column]))

    def test_empty_vector_array_with_custom_fill(self):
        # given
        custom_fill = numpy.array([0.1, 0.2, 0.4], dtype=numpy.float64)

        # when
        empty = empty_array(CUBA.VELOCITY, 23, fill=custom_fill)

        # then
        self.assertEqual(empty.shape, (23, 3))
        for index in range(23):
            assert_array_almost_equal(empty[index], [0.1, 0.2, 0.4])
