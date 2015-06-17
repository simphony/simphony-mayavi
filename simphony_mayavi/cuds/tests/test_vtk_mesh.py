import unittest
import uuid
import random

from simphony.cuds.mesh import Edge, Point, Face, Cell
from simphony.testing.utils import (
    create_points, grouper, create_data_container)
from simphony.testing.abc_check_mesh import (
    MeshPointOperationsCheck, MeshEdgeOperationsCheck,
    MeshFaceOperationsCheck, MeshCellOperationsCheck,
    MeshAttributesCheck)

from simphony_mayavi.cuds.api import VTKMesh
from simphony_mayavi.core.api import supported_cuba


class TestVTKMeshPointOperations(MeshPointOperationsCheck, unittest.TestCase):

    supported_cuba = supported_cuba()

    def container_factory(self, name):
        return VTKMesh(name=name)


class TestVTKMeshEdgeOperations(MeshEdgeOperationsCheck, unittest.TestCase):

    supported_cuba = supported_cuba()

    def setUp(self):
        points = create_points()
        more_points = create_points()
        for point in more_points:
            point.coordinates = [value * 2.0 for value in point.coordinates]
        self.points = points + more_points
        self.uids = [uuid.uuid4() for _ in self.points]
        for uid, point in zip(self.uids, self.points):
            point.uid = uid
        MeshEdgeOperationsCheck.setUp(self)

    def container_factory(self, name):
        container = VTKMesh(name=name)
        for point in self.points:
            container.add_point(point)
        return container

    def create_items(self):
        uids = self.uids
        return [Edge(
            points=puids,
            data=create_data_container(restrict=self.supported_cuba))
            for puids in grouper(uids, 2)]

    def create_item(self, uid):
        uids = self.uids
        return Edge(
            uid=uid,
            points=random.sample(uids, 2),
            data=create_data_container(restrict=self.supported_cuba))

    def test_update_item_points(self):
        # given
        container = self.container
        uids = self._add_items(container)
        item = self.get_operation(container, uids[2])
        point_uids = [
            container.add_point(Point((0.0, 0.0, 0.0)))
            for _ in range(self.points_range[-1])]
        # increasing
        for n in self.points_range:
            # when
            item.points = tuple(point_uids[:n])
            self.update_operation(container, item)

            # then
            retrieved = self.get_operation(container, item.uid)
            self.assertEqual(retrieved, item)
            self.assertNotEqual(item, self.item_list[2])
            self.assertNotEqual(retrieved, self.item_list[2])

        # decreasing
        for n in self.points_range[::-1]:
            # when
            item.points = tuple(point_uids[:n])
            self.update_operation(container, item)

            # then
            retrieved = self.get_operation(container, item.uid)
            self.assertEqual(retrieved, item)
            self.assertNotEqual(item, self.item_list[2])
            self.assertNotEqual(retrieved, self.item_list[2])


class TestVTKMeshFaceOperations(MeshFaceOperationsCheck, unittest.TestCase):

    supported_cuba = supported_cuba()

    def setUp(self):
        self.points = create_points()
        for multiplier in range(2, 5):
            more_points = create_points()
            for point in more_points:
                point.coordinates = [
                    value * multiplier for value in point.coordinates]
            self.points += more_points
        self.uids = [uuid.uuid4() for _ in self.points]
        for uid, point in zip(self.uids, self.points):
            point.uid = uid
        MeshFaceOperationsCheck.setUp(self)

    def container_factory(self, name):
        container = VTKMesh(name=name)
        for point in self.points:
            container.add_point(point)
        return container

    def create_items(self):
        uids = self.uids
        return [Face(
            points=puids,
            data=create_data_container(restrict=self.supported_cuba))
            for puids in grouper(uids, 3)]

    def create_item(self, uid):
        uids = self.uids
        return Face(
            uid=uid,
            points=random.sample(uids, 3),
            data=create_data_container(restrict=self.supported_cuba))

    def test_update_item_points(self):
        # given
        container = self.container
        uids = self._add_items(container)
        item = self.get_operation(container, uids[2])
        point_uids = [
            container.add_point(Point((0.0, 0.0, 0.0)))
            for _ in range(self.points_range[-1])]
        # increasing
        for n in self.points_range:
            # when
            item.points = tuple(point_uids[:n])
            self.update_operation(container, item)

            # then
            retrieved = self.get_operation(container, item.uid)
            self.assertEqual(retrieved, item)
            self.assertNotEqual(item, self.item_list[2])
            self.assertNotEqual(retrieved, self.item_list[2])

        # decreasing
        for n in self.points_range[::-1]:
            # when
            item.points = tuple(point_uids[:n])
            self.update_operation(container, item)

            # then
            retrieved = self.get_operation(container, item.uid)
            self.assertEqual(retrieved, item)
            self.assertNotEqual(item, self.item_list[2])
            self.assertNotEqual(retrieved, self.item_list[2])


class TestVTKMeshCellOperations(MeshCellOperationsCheck, unittest.TestCase):

    supported_cuba = supported_cuba()

    def setUp(self):
        self.points = create_points()
        for multiplier in range(2, 5):
            more_points = create_points()
            for point in more_points:
                point.coordinates = [
                    value * multiplier for value in point.coordinates]
            self.points += more_points
        self.uids = [uuid.uuid4() for _ in self.points]
        for uid, point in zip(self.uids, self.points):
            point.uid = uid
        MeshCellOperationsCheck.setUp(self)

    def container_factory(self, name):
        container = VTKMesh(name=name)
        for point in self.points:
            container.add_point(point)
        return container

    def create_items(self):
        uids = self.uids
        return [Cell(
            points=puids,
            data=create_data_container(restrict=self.supported_cuba))
            for puids in grouper(uids, 4)]

    def create_item(self, uid):
        uids = self.uids
        return Cell(
            uid=uid,
            points=random.sample(uids, 4),
            data=create_data_container(restrict=self.supported_cuba))

    def test_update_item_points(self):
        # given
        container = self.container
        uids = self._add_items(container)
        item = self.get_operation(container, uids[2])
        point_uids = [
            container.add_point(Point((0.0, 0.0, 0.0)))
            for _ in range(self.points_range[-1])]
        # increasing
        for n in self.points_range:
            # when
            item.points = tuple(point_uids[:n])
            self.update_operation(container, item)

            # then
            retrieved = self.get_operation(container, item.uid)
            self.assertEqual(retrieved, item)
            self.assertNotEqual(item, self.item_list[2])
            self.assertNotEqual(retrieved, self.item_list[2])

        # decreasing
        for n in self.points_range[::-1]:
            # when
            item.points = tuple(point_uids[:n])
            self.update_operation(container, item)

            # then
            retrieved = self.get_operation(container, item.uid)
            self.assertEqual(retrieved, item)
            self.assertNotEqual(item, self.item_list[2])
            self.assertNotEqual(retrieved, self.item_list[2])


class TestVTKMeshAttributes(MeshAttributesCheck, unittest.TestCase):

    def container_factory(self, name):
        return VTKMesh(name=name)

if __name__ == '__main__':
    unittest.main()
