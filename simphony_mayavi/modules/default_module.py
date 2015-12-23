import logging

from mayavi.modules.api import Surface, Glyph
from tvtk.tvtk_classes.sphere_source import SphereSource

from simphony.core.cuds_item import CUDSItem
from simphony.core.keywords import KEYWORDS
from simphony_mayavi.cuds.api import VTKLattice, VTKMesh, VTKParticles

logger = logging.getLogger(__name__)


def default_vector_module():
    ''' Returns a Glyph in its original mayavi defaults plus
    the scale_mode turned off
    '''
    module = Glyph()
    module.glyph.scale_mode="data_scaling_off"
    return module


def default_point_module():
    ''' Returns a Glyph with a sphere glyph source and
    scale_mode turned off.  Suitable for points/nodes
    with scalar data
    '''
    module = Glyph()
    module.glyph.scale_mode="data_scaling_off"
    module.glyph.glyph_source.glyph_source = SphereSource()
    return module


def default_face_module():
    module = Surface()
    return module


def default_module(vtk_cuds):
    if isinstance(vtk_cuds, VTKMesh) and vtk_cuds.element_data:
        return default_face_module()

    if len(vtk_cuds.point_data) == 0:
        logger.warning("No point data. Default module is a glyph")
        return default_vector_module()

    data_shapes = (KEYWORDS[cuba.name].shape
                   for cuba in vtk_cuds.point_data[0].keys())
    has_scalar = any((data_shape[0] == 1 for data_shape in data_shapes))
    if has_scalar:
        return default_point_module()
    else:
        return default_vector_module()
