import numpy

from simphony.core.cuba import CUBA

from simphony.cuds.particles import Particles, Particle
from simphony.cuds.lattice import make_tetragonal_lattice
from simphony.cuds.abc_particles import ABCParticles
from simphony.cuds.abc_mesh import ABCMesh
from simphony.cuds.abc_lattice import ABCLattice
from simphony.cuds.abc_modeling_engine import ABCModelingEngine


class DummyEngine(ABCModelingEngine):

    def __init__(self):
        self.datasets = {}
        # add lattice
        lattice = make_tetragonal_lattice("lattice", 0.2, 0.3, (5, 6, 10))
        new_node = []
        for node in lattice.iter_nodes():
            index = numpy.array(node.index) + 1.0
            node.data[CUBA.TEMPERATURE] = numpy.prod(index)
            new_node.append(node)
        lattice.update_nodes(new_node)
        self.datasets["lattice"] = lattice

        # add particles from lattice
        particles = Particles("particles")
        for node in lattice.iter_nodes():
            particles.add_particles([Particle(coordinates=node.index,
                                              data=node.data)])
        self.datasets["particles"] = particles
        self.time = 0.

    def run(self):
        self.time += 1.
        size = numpy.prod(self.get_dataset("lattice").size)

        # wobble particles and change temperature
        particles = self.get_dataset("particles")
        particle_list = []

        for index, particle in enumerate(particles.iter_particles()):
            particle.coordinates += numpy.random.uniform(-0.2, 0.2, 3)
            particle.data[CUBA.TEMPERATURE] = numpy.sin((index+self.time)/size)
            particle.data[CUBA.TEMPERATURE] *= size
            particle_list.append(particle)
        particles.update_particles(particle_list)

        # change the temperature of the lattice nodes
        lattice = self.get_dataset("lattice")
        size = numpy.prod(lattice.size)
        new_nodes = []
        for index, node in enumerate(lattice.iter_nodes()):
            node.data[CUBA.TEMPERATURE] = numpy.sin((index+self.time)/size)
            node.data[CUBA.TEMPERATURE] *= size
            new_nodes.append(node)
        lattice.update_nodes(new_nodes)

    def add_dataset(self, container):
        if not isinstance(container, (ABCParticles, ABCMesh, ABCLattice)):
            raise TypeError("container not supported")
        self.datasets[container.name] = container

    def remove_dataset(self, name):
        self.datasets.pop(name)

    def get_dataset(self, name):
        try:
            return self.datasets[name]
        except KeyError:
            raise ValueError("{} not found".format(name))

    def iter_datasets(self, names=None):
        if names is None:
            for dataset in self.datasets.itervalues():
                yield dataset
        else:
            for name in names:
                yield self.get_dataset(name)

    def get_dataset_names(self):
        return self.datasets.keys()
