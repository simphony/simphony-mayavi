from mayavi import mlab

from simphony.cuds.abc_mesh import ABCMesh
from simphony.cuds.abc_particles import ABCParticles
from simphony.cuds.abc_lattice import ABCLattice

from simphony_mayavi.sources.api import CUDSSource
from simphony_mayavi.modules.default_module import default_module


def show(cuds):
    """ Show the cuds objects using the default visualisation.

     Parameters
     ----------
     cuds :
         A top level cuds object (e.g. a mesh). The method will detect
         the type of object and create the appropriate visualisation.

    """
    if isinstance(cuds, (ABCMesh, ABCParticles, ABCLattice)):
        source = CUDSSource(cuds=cuds)
    else:
        msg = 'Provided object {} is not of any known cuds type'
        raise TypeError(msg.format(type(cuds)))

    modules = default_module(source)

    # add source
    mayavi_engine = mlab.get_engine()
    mayavi_engine.add_source(source)
    # add default modules
    for module in modules:
        mayavi_engine.add_module(module)

    mlab.show()
