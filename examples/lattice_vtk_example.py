import numpy

from simphony.core.cuba import CUBA
from simphony.cuds.primitive_cell import PrimitiveCell
from simphony.visualisation import mayavi_tools

cubic = mayavi_tools.VTKLattice.empty(
    "test", PrimitiveCell.for_cubic_lattice(0.1),
    (5, 10, 12), (5, 4, 0))

hexagonal = mayavi_tools.VTKLattice.empty(
    "test", PrimitiveCell.for_hexagonal_lattice(0.1, 0.05),
    (5, 10, 12), (5, 4, 0))

bcc = mayavi_tools.VTKLattice.empty(
    "test", PrimitiveCell.for_body_centered_cubic_lattice(0.1),
    (5, 10, 12), (5, 4, 0))

lattice = bcc

new_nodes = []
for node in lattice.iter_nodes():
    index = numpy.array(node.index) + 1.0
    node.data[CUBA.TEMPERATURE] = numpy.prod(index)
    new_nodes.append(node)

lattice.update_nodes(new_nodes)


if __name__ == '__main__':

    # Visualise the Lattice object
    mayavi_tools.show(lattice)
