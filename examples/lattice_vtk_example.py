import numpy

from simphony.core.cuba import CUBA
from simphony.cuds.primitive_cell import PrimitiveCell
from simphony.visualisation import mayavi_tools

cubic = mayavi_tools.VTKLattice.empty(
    "test", PrimitiveCell.for_cubic_lattice(0.1),
    (5, 10, 12), (0, 0, 0))

lattice = cubic

new_nodes = []
for node in lattice.iter(item_type=CUBA.NODE):
    index = numpy.array(node.index) + 1.0
    node.data[CUBA.TEMPERATURE] = numpy.prod(index)
    new_nodes.append(node)

lattice.update(new_nodes)


if __name__ == '__main__':

    # Visualise the Lattice object
    mayavi_tools.show(lattice)
