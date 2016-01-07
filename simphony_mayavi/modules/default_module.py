import logging

from mayavi.modules.api import Surface, Glyph
from mayavi.tools.tools import _typical_distance
from tvtk.tvtk_classes.sphere_source import SphereSource

from simphony.cuds.abc_mesh import ABCMesh


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


def default_module(source):
    ''' Mapping for module appropriate for the selected data

    Parameters
    ----------
    source : CUDSSource

    Returns
    -------
    modules : list of mayavi.modules to be added to the pipeline
    '''
    modules = []

    scale_factor = _typical_distance(source.data) * 0.5

    if source.point_scalars_name:
        if isinstance(source.cuds, ABCMesh):
            modules.append(Surface())
        else:
            modules.append(default_scalar_module(scale_factor))
    if source.point_vectors_name:
        modules.append(default_vector_module())
    if source.cell_scalars_name:
        modules.append(Surface())
    if source.cell_vectors_name:
        modules.append(default_vector_module())

    if modules:
        return modules
    else:
        message = "Unknown scalar/vector data for setting default module"
        logging.warning(message)
        return [default_scalar_module(scale_factor)]
