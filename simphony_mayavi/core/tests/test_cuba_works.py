import unittest

import numpy
from numpy.testing import assert_array_almost_equal
from simphony.core.keywords import KEYWORDS
from simphony.core.cuba import CUBA

from simphony_mayavi.core.utils import CUBAWorks


class TestCubaWorks(unittest.TestCase):

    def test_default_initialization(self):
        cuba_works = CUBAWorks.default()

        float_scalar_cuba = [
            cuba for cuba in CUBA
            if KEYWORDS[cuba.name].shape == [1] and numpy.issubdtype(
                KEYWORDS[cuba.name].dtype, numpy.float)]

        int_scalar_cuba = [
            cuba for cuba in CUBA
            if KEYWORDS[cuba.name].shape == [1] and numpy.issubdtype(
                KEYWORDS[cuba.name].dtype, numpy.int)]

        float_vector_cuba = [
            cuba for cuba in CUBA
            if KEYWORDS[cuba.name].shape == [3] and numpy.issubdtype(
                KEYWORDS[cuba.name].dtype, numpy.float)]

        int_vector_cuba = [
            cuba for cuba in CUBA
            if KEYWORDS[cuba.name].shape == [3] and numpy.issubdtype(
                KEYWORDS[cuba.name].dtype, numpy.int)]

        expected = (
            float_scalar_cuba + int_scalar_cuba +
            float_vector_cuba + int_vector_cuba)

        self.assertItemsEqual(cuba_works.supported, expected)
        for cuba in float_scalar_cuba:
            self.assertTrue(numpy.isnan(cuba_works.defaults[cuba]))
        for cuba in int_scalar_cuba:
            self.assertEqual(cuba_works.defaults[cuba], -1)
        for cuba in float_vector_cuba:
            default = cuba_works.defaults[cuba]
            for value in default:
                self.assertTrue(numpy.isnan(value))
        for cuba in int_vector_cuba:
            self.assertEqual(cuba_works.defaults[cuba], -1)

    def test_with_custom_cuba_keys(self):
        cuba_works = CUBAWorks.custom(
            supported=[CUBA.RADIUS, CUBA.MASS, CUBA.VELOCITY])

        expected = {
            CUBA.RADIUS: numpy.nan,
            CUBA.MASS: numpy.nan,
            CUBA.VELOCITY: numpy.array(
                [numpy.nan, numpy.nan, numpy.nan], dtype=numpy.float64)}
        self.assertEqual(len(cuba_works.defaults), 3)
        for key in expected:
            assert_array_almost_equal(cuba_works.defaults[key], expected[key])

    def test_with_custom_cuba_keys_and_defaults(self):
        defaults = {
            CUBA.RADIUS: (5, 56),
            CUBA.MASS: 7,
            CUBA.VELOCITY: numpy.array(
                [0.1, 0.2, 0.4], dtype=numpy.float64)}
        cuba_works = CUBAWorks.custom(
            supported=[CUBA.RADIUS, CUBA.VELOCITY],
            defaults=defaults)

        self.assertEqual(len(cuba_works.defaults), 2)
        for key in [CUBA.RADIUS, CUBA.VELOCITY]:
            assert_array_almost_equal(cuba_works.defaults[key], defaults[key])

    def test_empty_scalar_array(self):
        # given
        cuba_works = CUBAWorks.custom(
            supported=[CUBA.RADIUS, CUBA.VELOCITY])

        # when
        empty = cuba_works.empty_array(CUBA.RADIUS, 23)

        # then
        self.assertEqual(empty.shape, (23, 1))
        for index in range(23):
            self.assertTrue(numpy.isnan(empty[index]))

    def test_empty_vector_array(self):
        # given
        cuba_works = CUBAWorks.custom(
            supported=[CUBA.RADIUS, CUBA.VELOCITY])

        # when
        empty = cuba_works.empty_array(CUBA.VELOCITY, 23)

        # then
        self.assertEqual(empty.shape, (23, 3))
        for index in range(23):
            for column in range(3):
                self.assertTrue(numpy.isnan(empty[index, column]))

    def test_empty_vector_array_with_custom_fill(self):
        # given
        defaults = {
            CUBA.RADIUS: (5, 56),
            CUBA.VELOCITY: numpy.array(
                [0.1, 0.2, 0.4], dtype=numpy.float64)}
        cuba_works = CUBAWorks.custom(
            supported=[CUBA.RADIUS, CUBA.VELOCITY],
            defaults=defaults)

        # when
        empty = cuba_works.empty_array(CUBA.VELOCITY, 23)

        # then
        self.assertEqual(empty.shape, (23, 3))
        for index in range(23):
            assert_array_almost_equal(empty[index], [0.1, 0.2, 0.4])

    def test_empty_array_not_supported(self):
        # given
        defaults = {
            CUBA.RADIUS: (5, 56),
            CUBA.VELOCITY: numpy.array(
                [0.1, 0.2, 0.4], dtype=numpy.float64)}
        cuba_works = CUBAWorks.custom(
            supported=[CUBA.RADIUS, CUBA.VELOCITY],
            defaults=defaults)

        # when/then
        with self.assertRaises(ValueError):
            cuba_works.empty_array(CUBA.MASS, 23)
