from mayavi import mlab
from mayavi.tools.tools import _typical_distance

from simphony.cuds.abc_mesh import ABCMesh
from simphony.cuds.abc_particles import ABCParticles
from simphony.cuds.abc_lattice import ABCLattice
from simphony.cuds.abc_modeling_engine import ABCModelingEngine

from simphony_mayavi.sources.api import CUDSSource
from simphony_mayavi.sources.api import EngineSource


def show(cuds):
    """ Show the cuds objects using the default visualisation.

     Parameters
     ----------
     cuds :
         A top level cuds object (e.g. a mesh). The method will detect
         the type of object and create the appropriate visualisation.

    """
    if isinstance(cuds, ABCMesh):
        source = CUDSSource(cuds=cuds)
        mlab.pipeline.surface(source, name=cuds.name)
    elif isinstance(cuds, ABCParticles):
        source = CUDSSource(cuds=cuds)
        scale_factor = _typical_distance(source.data) * 0.5
        mlab.pipeline.glyph(
            source, name=cuds.name,
            scale_factor=scale_factor, scale_mode='none')
        surface = mlab.pipeline.surface(source)
        surface.actor.mapper.scalar_visibility = False
    elif isinstance(cuds, ABCLattice):
        source = CUDSSource(cuds=cuds)
        scale_factor = _typical_distance(source.data) * 0.5
        mlab.pipeline.glyph(
            source, name=cuds.name,
            scale_factor=scale_factor, scale_mode='none')
    elif isinstance(cuds, ABCModelingEngine):
        source = EngineSource(engine=cuds)
        if source.datasets:
            source.dataset = source.datasets[0]
        scale_factor = _typical_distance(source.data) * 0.5
        mlab.pipeline.glyph(
            source,
            scale_factor=scale_factor, scale_mode='none')
    else:
        msg = 'Provided object {} is not of any known cuds type'
        raise TypeError(msg.format(type(cuds)))
    mlab.show()
