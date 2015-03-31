import sys

from mayavi.api import OffScreenEngine
from mayavi.tools.tools import _typical_distance
from mayavi.modules.api import Glyph, Surface
from mayavi.core.api import Engine

from simphony.cuds.abstractmesh import ABCMesh
from simphony.cuds.abstractparticles import ABCParticles
from simphony.cuds.abstractlattice import ABCLattice

from simphony_mayavi.sources.api import (
    ParticlesSource, MeshSource, LatticeSource)


def snapshot(cuds, filename):
    """ Shave a snapshot of the cuds object using the default visualisation.

     Parameters
     ----------
     cuds :
         A top level cuds object (e.g. a mesh). The method will detect
         the type of object and create the appropriate visualisation.

     filename : string
         The filename to use for the output file.

    """
    size = 800, 600

    if sys.platform != 'win32':
        _snapshot_windows(cuds, filename, size)
    else:
        # The OffScreenEngine does not reliably work for linux/mac-os
        _snapshot_linux(cuds, filename, size)


def _snapshot_windows(cuds, filename, size):
    engine = OffScreenEngine()
    engine.start()
    try:
        if isinstance(cuds, ABCMesh):
            source = MeshSource.from_mesh(cuds)
            window = engine.new_scene()
            engine.add_source(source)
            engine.add_module(Surface())
        elif isinstance(cuds, ABCParticles):
            source = ParticlesSource.from_particles(cuds)
            engine = OffScreenEngine()
            engine.start()
            window = engine.new_scene()
            engine.add_source(source)
            module = Glyph()
            glyph_source = module.glyph.glyph_source
            glyph_source.glyph_source = \
                glyph_source.glyph_dict['sphere_source']
            module.glyph.glyph.scale_factor = \
                _typical_distance(source.data) * 0.5
            module.glyph.scale_mode = 'data_scaling_off'
            engine.add_module(module)
            module = Surface()
            module.actor.mapper.scalar_visibility = False
            engine.add_module(module)
        elif isinstance(cuds, ABCLattice):
            source = LatticeSource.from_lattice(cuds)
            engine = OffScreenEngine()
            engine.start()
            window = engine.new_scene()
            engine.add_source(source)
            module = Glyph()
            glyph_source = module.glyph.glyph_source
            glyph_source.glyph_source = \
                glyph_source.glyph_dict['sphere_source']
            module.glyph.glyph.scale_factor = \
                _typical_distance(source.data) * 0.5
            module.glyph.scale_mode = 'data_scaling_off'
            engine.add_module(module)
        else:
            msg = 'Provided object {} is not of any known cuds type'
            raise TypeError(msg.format(type(cuds)))

        # Use some default values for the camera
        camera = window.scene.camera
        camera.azimuth(45)
        camera.elevation(30)
        window.scene.reset_zoom()
        window.scene.save(filename, size)
    finally:
        engine.stop()


def _snapshot_linux(cuds, filename, size):
    width, height = size
    from mayavi import mlab
    if isinstance(cuds, ABCMesh):
        source = MeshSource.from_mesh(cuds)
        mlab.options.offscreen = True
        mlab.pipeline.surface(source, name=cuds.name)
    elif isinstance(cuds, ABCParticles):
        source = ParticlesSource.from_particles(cuds)
        scale_factor = _typical_distance(source.data) * 0.5
        mlab.options.offscreen = True
        mlab.pipeline.glyph(
            source, name=cuds.name,
            scale_factor=scale_factor, scale_mode='none')
        surface = mlab.pipeline.surface(source)
        surface.actor.mapper.scalar_visibility = False
    elif isinstance(cuds, ABCLattice):
        source = LatticeSource.from_lattice(cuds)
        scale_factor = _typical_distance(source.data) * 0.5
        mlab.options.offscreen = True
        mlab.pipeline.glyph(
            source, name=cuds.name,
            scale_factor=scale_factor, scale_mode='none')
    else:
        msg = 'Provided object {} is not of any known cuds type'
        raise TypeError(msg.format(type(cuds)))
    mlab.savefig(filename, (width, height), magnification=1.0)
    mlab.clf()
    mlab.close()
