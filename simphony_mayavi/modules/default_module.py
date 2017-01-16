import logging

from mayavi.modules.api import Surface, Glyph
from mayavi.tools.tools import _typical_distance
from tvtk.tvtk_classes.sphere_source import SphereSource

from simphony.core.cuba import CUBA
from simphony.cuds.abc_mesh import ABCMesh
from simphony.cuds.abc_particles import ABCParticles

logger = logging.getLogger(__name__)


def default_vector_module(scale_factor=1.):
    ''' Returns a Glyph in its original mayavi defaults plus
    the scale_mode turned off
    '''
    module = Glyph()
    module.glyph.scale_mode = "data_scaling_off"
    module.glyph.color_mode = "color_by_vector"
    module.glyph.glyph_source.glyph_source.scale *= scale_factor
    return module


def default_scalar_module(scale_factor=1.):
    ''' Returns a Glyph with a sphere glyph source and
    scale_mode turned off.  Suitable for points/nodes
    with scalar data
    '''
    module = Glyph()
    module.glyph.scale_mode = "data_scaling_off"
    module.glyph.glyph_source.glyph_source = SphereSource()
    module.glyph.glyph_source.glyph_source.radius *= scale_factor
    return module


def default_bond_module():
    module = Surface()
    module.actor.mapper.scalar_visibility = False
    return module


def default_module(source):
    ''' Mapping for module appropriate for the selected data

    Parameters
    ----------
    source : CUDSSource

    Returns
    -------
    modules : list
        mayavi modules to be added to the pipeline
    '''
    modules = []

    scale_factor = _typical_distance(source.data) * 0.5

    # default module for point scalars
    if source.point_scalars_name:
        if isinstance(source.cuds, ABCMesh):
            modules.append(Surface())
        else:
            modules.append(default_scalar_module(scale_factor))

    # default module for point vectors
    if source.point_vectors_name:
        modules.append(default_vector_module())

    # default module for cell scalars
    if source.cell_scalars_name:
        modules.append(Surface())

    # default module for cell vectors
    if source.cell_vectors_name:
        modules.append(default_vector_module())

    # default module for particle bonds
    if (isinstance(source.cuds, ABCParticles) and
            source.cuds.count_of(CUBA.BOND) > 0):
        modules.append(default_bond_module())

    if modules:
        return modules
    else:
        message = "Unknown scalar/vector data for setting default module"
        logger.warning(message)
        return [default_scalar_module(scale_factor)]
