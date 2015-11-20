import numpy

from simphony.cuds.lattice import make_cubic_lattice
from simphony.core.cuba import CUBA

lattice = make_cubic_lattice('test', 0.1, (5, 10, 12))

new_nodes = []
for node in lattice.iter_nodes():
    index = numpy.array(node.index) + 1.0
    node.data[CUBA.TEMPERATURE] = numpy.prod(index)
    new_nodes.append(node)

lattice.update_nodes(new_nodes)


if __name__ == '__main__':
    from simphony.visualisation import mayavi_tools

    # Visualise the Lattice object
    mayavi_tools.show(lattice)
