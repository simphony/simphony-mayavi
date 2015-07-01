from mayavi.sources.vtk_data_source import VTKDataSource
from traits.api import Dict

from simphony_mayavi.cuds.api import VTKMesh


class MeshSource(VTKDataSource):
    """ SimPhoNy CUDS Mesh container to Mayavi Source converter

    """

    #: The mapping from the point uid to the vtk points array.
    point2index = Dict

    #: The mapping from the element uid to the vtk cell index.
    element2index = Dict

    @classmethod
    def from_mesh(cls, mesh):
        """ Return a MeshSource from a CUDS Mesh container.

        Parameters
        ----------
        mesh : Mesh
            The CUDS Mesh instance to copy the information from.

        """
        if not isinstance(mesh, VTKMesh):
            mesh = VTKMesh.from_mesh(mesh)
        data = mesh.data_set
        point2index = mesh.point2index
        element2index = mesh.element2index

        return cls(
            data=data,
            point2index=point2index,
            element2index=element2index)
