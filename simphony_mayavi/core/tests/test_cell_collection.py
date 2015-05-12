import unittest

from tvtk.api import tvtk

from simphony_mayavi.core.cell_collection import CellCollection


class TestCellCollection(unittest.TestCase):

    def setUp(self):
        self.cells = [
            [0, 1, 2, 3],
            [4, 5, 6, 7, 8, 9, 10, 11],
            [2, 7, 11],
            [1, 4],
            [1, 5, 8]]
        self.cell_types = [
            tvtk.Tetra(),
            tvtk.Hexahedron(),
            tvtk.Triangle(),
            tvtk.Line(),
            tvtk.PolyLine()]


        self.vtk = tvtk.CellArray()
        self.vtk.from_array(self.cells)

    def test_length(self):
        # when
        collection = CellCollection()

        # then
        self.assertEqual(len(collection), 0)

        # when
        array = tvtk.CellArray()
        array.insert_next_cell(tvtk.Line())
        array.insert_next_cell(tvtk.Line())
        collection = CellCollection(cell_array=array)

        # then
        self.assertEqual(len(collection), 2)

    def test_getitem(self):
        # given
        cells = self.cells
        collection = CellCollection(self.vtk)

        # when/then
        for index in range(5):
            self.assertSequenceEqual(collection[index], cells[index])

        # when/then
        with self.assertRaises(IndexError):
            collection[5]

    def test_getitem_with_long_int_index(self):
        # given
        cells = self.cells
        collection = CellCollection(self.vtk)

        # when/then
        for index in range(5):
            self.assertSequenceEqual(collection[long(index)], cells[index])

        # when/then
        with self.assertRaises(IndexError):
            collection[long(5)]

    def test_setitem_with_same_number_of_points(self):
        # given
        cells = self.cells[:]
        collection = CellCollection(self.vtk)

        # when
        collection[2] = [3, 56, 12]

        # when/then
        cells[2] = [3, 56, 12]
        for index in range(5):
            self.assertSequenceEqual(collection[index], cells[index])
        self.assertEqual(len(collection), 5)

    def test_setitem_with_fewer_number_of_points(self):
        # given
        cells = self.cells[:]
        collection = CellCollection(self.vtk)

        # when
        collection[2] = [3, 56]

        # when/then
        cells[2] = [3, 56]
        for index in range(5):
            self.assertSequenceEqual(collection[index], cells[index])
        self.assertEqual(len(collection), 5)

    def test_setitem_with_more_points(self):
        # given
        cells = self.cells[:]
        collection = CellCollection(self.vtk)

        # when
        collection[2] = [3, 56, 14, 1]

        # when/then
        cells[2] = [3, 56, 14, 1]
        for index in range(5):
            self.assertSequenceEqual(collection[index], cells[index])
        self.assertEqual(len(collection), 5)

    def test_delitem(self):
        # given
        cells = self.cells[:]
        collection = CellCollection(self.vtk)

        # when
        del collection[1]

        # when/then
        del cells[1]
        for index in range(4):
            self.assertSequenceEqual(collection[index], cells[index])
        self.assertEqual(len(collection), 4)

    def test_append(self):
        # given
        cells = self.cells[:]
        collection = CellCollection(self.vtk)

        # when
        collection.append([2, 3, 5, 12, 1003])

        # when/then
        cells.append([2, 3, 5, 12, 1003])
        for index in range(6):
            self.assertSequenceEqual(collection[index], cells[index])
        self.assertEqual(len(collection), 6)

    def test_insert(self):
        # given
        cells = self.cells[:]
        collection = CellCollection(self.vtk)

        # when
        collection.insert(1, [2, 3, 5, 12, 1003])

        # when/then
        cells.insert(1, [2, 3, 5, 12, 1003])
        for index in range(6):
            self.assertSequenceEqual(collection[index], cells[index])
        self.assertEqual(len(collection), 6)
