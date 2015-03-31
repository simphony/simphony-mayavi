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
    """ Shave a snapshot of the cuds object using the default visualization.

     Parameters
     ----------
     cuds :
         A top level cuds object (e.g. a mesh). The method will detect
         the type of object and create the appropriate visualisation.

     filename : string
         The filename to use for the output file.

    """
    size = 800, 600

    if sys.platform == 'win32':
        engine = OffScreenEngine()
    else:
        # The OffScreenEngine does not reliably work for linux/mac-os
        engine = Engine()

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
