from mayavi.sources.vtk_data_source import VTKDataSource

from simphony_mayavi.cuds.api import VTKLattice


class LatticeSource(VTKDataSource):
    """ SimPhoNy CUDS Lattice container to Mayavi Source converter

    """

    @classmethod
    def from_lattice(cls, lattice):
        """ Return a LatticeSource from a CUDS Lattice container.

        Parameters
        ----------
        lattice : Lattice
            The cuds Lattice instance to copy the information from.

        """
        if not isinstance(lattice, VTKLattice):
            lattice = VTKLattice.from_lattice(lattice)
        return cls(data=lattice.data_set)
