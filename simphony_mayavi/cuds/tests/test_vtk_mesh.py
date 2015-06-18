import unittest

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

    def container_factory(self, name):
        container = VTKMesh(name=name)
        for point in self.points:
            container.add_point(point)
        return container


class TestVTKMeshFaceOperations(MeshFaceOperationsCheck, unittest.TestCase):

    supported_cuba = supported_cuba()

    def container_factory(self, name):
        container = VTKMesh(name=name)
        for point in self.points:
            container.add_point(point)
        return container


class TestVTKMeshCellOperations(MeshCellOperationsCheck, unittest.TestCase):

    supported_cuba = supported_cuba()

    def container_factory(self, name):
        container = VTKMesh(name=name)
        for point in self.points:
            container.add_point(point)
        return container


class TestVTKMeshAttributes(MeshAttributesCheck, unittest.TestCase):

    def container_factory(self, name):
        return VTKMesh(name=name)

if __name__ == '__main__':
    unittest.main()
