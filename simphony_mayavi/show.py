from mayavi import mlab
from mayavi.tools.tools import _typical_distance

from simphony.cuds.abstractmesh import ABCMesh
from simphony.cuds.abstractparticles import ABCParticles
from simphony.cuds.abstractlattice import ABCLattice

from simphony_mayavi.sources.api import (
    ParticlesSource, MeshSource, LatticeSource)


def show(cuds):

    if isinstance(cuds, ABCMesh):
        source = MeshSource.from_mesh(cuds)
        mlab.pipeline.surface(source, name=cuds.name)
    elif isinstance(cuds, ABCParticles):
        source = ParticlesSource.from_particles(cuds)
        scale_factor = _typical_distance(source.data) * 0.5
        mlab.pipeline.glyph(
            source, name=cuds.name,
            scale_factor=scale_factor, scale_mode='none')
        mlab.pipeline.surface(source)
    elif isinstance(cuds, ABCLattice):
        source = LatticeSource.from_lattice(cuds)
        scale_factor = _typical_distance(source.data) * 0.5
        mlab.pipeline.glyph(
            source, name=cuds.name,
            scale_factor=scale_factor, scale_mode='none')
    else:
        msg = 'Provided object {} is not of any known cuds type'
        raise TypeError(msg.format(type(cuds)))
    mlab.show()
