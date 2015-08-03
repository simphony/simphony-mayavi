import numpy

from simphony.core.cuba import CUBA
from simphony_mayavi.cuds.api import VTKLattice

lattice = VTKLattice.empty(
    'test', 'Cubic', (0.1, 0.1, 0.1), (5, 10, 12), (0, 0, 0))

for node in lattice.iter_nodes():
    index = numpy.array(node.index) + 1.0
    node.data[CUBA.TEMPERATURE] = numpy.prod(index)
    lattice.update_node(node)


if __name__ == '__main__':
    from simphony.visualisation import mayavi_tools

    # Visualise the Lattice object
    mayavi_tools.show(lattice)