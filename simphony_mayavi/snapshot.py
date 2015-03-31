from mayavi import mlab
from mayavi.tools.tools import _typical_distance

from simphony.cuds.abstractmesh import ABCMesh
from simphony.cuds.abstractparticles import ABCParticles
from simphony.cuds.abstractlattice import ABCLattice

from simphony_mayavi.sources.api import (
    ParticlesSource, MeshSource, LatticeSource)


def snapshot(cuds, filename):
    """ Shave a snapshot of the cuds object using the default visualization.

     Parameters
     ----------
     cuds :
         A top level cuds object (e.g. a mesh). The method will detect
         the type of object and create the appropriate visualisation.

     filename : string
         The filename to use for the output file.

    """
    if isinstance(cuds, ABCMesh):
        source = MeshSource.from_mesh(cuds)
        mlab.options.offsceen = True
        mlab.pipeline.surface(source, name=cuds.name)
    elif isinstance(cuds, ABCParticles):
        source = ParticlesSource.from_particles(cuds)
        scale_factor = _typical_distance(source.data) * 0.5
        mlab.options.offsceen = True
        mlab.pipeline.glyph(
            source, name=cuds.name,
            scale_factor=scale_factor, scale_mode='none')
        surface = mlab.pipeline.surface(source)
        surface.actor.mapper.scalar_visibility = False
    elif isinstance(cuds, ABCLattice):
        source = LatticeSource.from_lattice(cuds)
        scale_factor = _typical_distance(source.data) * 0.5
        mlab.options.offsceen = True
        mlab.pipeline.glyph(
            source, name=cuds.name,
            scale_factor=scale_factor, scale_mode='none')
    else:
        msg = 'Provided object {} is not of any known cuds type'
        raise TypeError(msg.format(type(cuds)))
    mlab.savefig(filename)
