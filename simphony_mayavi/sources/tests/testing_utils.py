import numpy

from simphony.core.cuba import CUBA
from simphony.core.cuds_item import CUDSItem

from simphony.core.data_container import DataContainer
from simphony.cuds.mesh import Mesh, Face, Point
from simphony.cuds.particles import Particles, Particle
from simphony.cuds.lattice import make_tetragonal_lattice
from simphony.cuds.abc_particles import ABCParticles
from simphony.cuds.abc_mesh import ABCMesh
from simphony.cuds.abc_lattice import ABCLattice
from simphony.cuds.abc_modeling_engine import ABCModelingEngine

from simphony_mayavi.core.doc_utils import mergedocs


@mergedocs(ABCModelingEngine)
class DummyEngine(ABCModelingEngine):
    ''' Simulate a modeling engine for tests
    On initialisation an engine contains three datasets: "particles",
    "lattice" and "mesh". Contents in each of these datasets evolve
    each time when ``run`` is called.
    '''

    def __init__(self):
        self.datasets = {}
        self.time = 0.
        self.CM = DataContainer()
        self.SP = DataContainer()
        self.BC = DataContainer()
        self.CM[CUBA.TIME_STEP] = 1.
        self.CM[CUBA.NUMBER_OF_TIME_STEPS] = 10

        # add lattice with temperature, mass and velocity data
        lattice = make_tetragonal_lattice("lattice", 1., 1.1, (4, 5, 6))
        size = numpy.prod(lattice.size)
        new_node = []
        for node in lattice.iter_nodes():
            index = numpy.prod(numpy.array(node.index)) + 1.0
            node.data[CUBA.TEMPERATURE] = numpy.sin(index/size/2.)*size
            node.data[CUBA.MASS] = index
            node.data[CUBA.VELOCITY] = numpy.random.uniform(-0.1, 0.1, 3)
            new_node.append(node)
        lattice.update_nodes(new_node)
        self.datasets["lattice"] = lattice

        # add particles from lattice
        particles = Particles("particles")
        for node in lattice.iter_nodes():
            particles.add_particles([Particle(coordinates=node.index,
                                              data=node.data)])
        self.datasets["particles"] = particles

        # add mesh
        mesh = Mesh("mesh")
        points = numpy.array([
            [0, 0, 0], [1, 0, 0], [0, 1, 0], [0, 0, 1],
            [2, 0, 0], [3, 0, 0], [3, 1, 0], [2, 1, 0],
            [2, 0, 1], [3, 0, 1], [3, 1, 1], [2, 1, 1]], 'f')
        faces = [[2, 7, 11]]
        # add points
        point_iter = (Point(coordinates=point,
                            data=DataContainer(TEMPERATURE=index))
                      for index, point in enumerate(points))
        uids = mesh.add_points(point_iter)
        face_iter = (Face(points=[uids[index] for index in element],
                          data=DataContainer(VELOCITY=(index, 0., 0.)))
                     for index, element in enumerate(faces))
        mesh.add_faces(face_iter)
        self.datasets["mesh"] = mesh

    def run(self):
        delta_t = self.CM[CUBA.TIME_STEP]*self.CM[CUBA.NUMBER_OF_TIME_STEPS]
        self.time += delta_t

        mappings = {
            ABCLattice:
                ("iter_nodes", CUDSItem.NODE, "update_nodes", "index"),
            ABCMesh:
                ("iter_points", CUDSItem.POINT, "update_points",
                 "coordinates"),
            ABCParticles:
                ("iter_particles", CUDSItem.PARTICLE, "update_particles",
                 "coordinates")
        }
        for dataset in self.datasets.values():
            # get parent class
            parent = dataset.__class__.__mro__[1]

            iter_func, cudsitem, update_fun, index_name = mappings[parent]

            # list of items in the datasets
            item_list = [item for item in getattr(dataset, iter_func)()]
            # number of items
            size = dataset.count_of(cudsitem)
            # function for updating items
            update_fun = getattr(dataset, update_fun)

            # if items have "coordinates", wobblem them
            if hasattr(item_list[0], "coordinates"):
                new_items = []
                for item in item_list:
                    delta = numpy.random.uniform(-0.05, 0.05, 3)
                    item.data[CUBA.VELOCITY] = delta
                    item.coordinates += delta
                    new_items.append(item)
                item_list = new_items

            # change temperature for all items
            new_items = []
            for item in item_list:
                index = numpy.prod(getattr(item, index_name)) + 1.0
                temperature = numpy.sin((index+self.time)/size/2.)*size
                item.data[CUBA.TEMPERATURE] = temperature
                new_items.append(item)
            update_fun(new_items)

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
