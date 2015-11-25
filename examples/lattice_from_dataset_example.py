import numpy

from tvtk.api import tvtk
from mayavi.scripts import mayavi2
from simphony.core.cuba import CUBA
from simphony.cuds.primitive_cell import PrimitiveCell

from simphony.visualisation import mayavi_tools

datasets = []

# Size of sample lattices
size = (5, 4, 10)

# tvtk.ImageData Examples
# Cubic lattice
data_set = tvtk.ImageData(spacing=(0.1, 0.1, 0.1), origin=(0., 0., 0.))
data_set.extent = 0, size[0] - 1, 0, size[1] - 1, 0, size[2] - 1
datasets.append(data_set)

# Tetragonal
data_set = tvtk.ImageData(spacing=(0.1, 0.1, 0.3), origin=(0., 0., 0.))
data_set.extent = 0, size[0] - 1, 0, size[1] - 1, 0, size[2] - 1
datasets.append(data_set)


# Orthorhombic-P
data_set = tvtk.ImageData(spacing=(0.1, 0.2, 0.3), origin=(0., 0., 0.))
data_set.extent = 0, size[0] - 1, 0, size[1] - 1, 0, size[2] - 1
datasets.append(data_set)


# tvtk.PolyData Examples
def create_polydata_from_pc(p1, p2, p3, size=(5, 10, 12)):
    ''' Create a tvtk.PolyData given a set of primitive vectors
    and size'''
    y, z, x = numpy.meshgrid(
    range(size[1]), range(size[2]), range(size[0]))
    points = numpy.zeros(shape=(x.size, 3), dtype='double')
    for idim in range(3):
        points[:, idim] += p1[idim]*x.ravel() +\
            p2[idim]*y.ravel() +\
            p3[idim]*z.ravel()
    return tvtk.PolyData(points=points)


def rotate_primitive_cell(pc, angle1=numpy.pi/2., angle2=0.):
    ''' Rotate the given primitive cell ``pc`` for ``angle1`` about z
    and then for ``angle2`` about x
    '''
    # rotate x-y for angle1 about z
    xy_rot = numpy.array([[numpy.cos(angle1), numpy.sin(angle1), 0],
                          [numpy.sin(-angle1), numpy.cos(angle1), 0],
                          [0, 0, 1]])
    # rotate y-z for angle2 about x
    yz_rot = numpy.array([[1, 0, 0],
                          [0, numpy.cos(angle2), numpy.sin(angle2)],
                          [0, numpy.sin(-angle2), numpy.cos(angle2)]])
    # rotate x-y, then y-z
    xyz_rot = numpy.matmul(yz_rot, xy_rot)
    return tuple(numpy.matmul(xyz_rot, p) for p in (pc.p1, pc.p2, pc.p3))


# Test the mirror images too

# a cubic lattice on a rotated coordinates represented using PolyData
datasets.append(create_polydata_from_pc(
    *rotate_primitive_cell(
        PrimitiveCell.for_cubic_lattice(1.))))

# BCC lattice in a rotated coor. sys.
datasets.append(create_polydata_from_pc(*rotate_primitive_cell(
            PrimitiveCell.for_body_centered_cubic_lattice(1.))))

# FCC lattice in a rotated coor. sys.
datasets.append(create_polydata_from_pc(*rotate_primitive_cell(
            PrimitiveCell.for_face_centered_cubic_lattice(1.))))

# rhombohedral lattice in a rotated coor. sys.
datasets.append(create_polydata_from_pc(*rotate_primitive_cell(
            PrimitiveCell.for_rhombohedral_lattice(1., 1.))))

# tetragonal lattice in a rotated coor. sys.
datasets.append(create_polydata_from_pc(*rotate_primitive_cell(
            PrimitiveCell.for_tetragonal_lattice(0.5, 1.))))

# body_centered_tetragonal lattice in a rotated coor. sys.
datasets.append(create_polydata_from_pc(*rotate_primitive_cell(
            PrimitiveCell.for_body_centered_tetragonal_lattice(1., 1.))))

# hexagonal lattice in a rotated coor. sys.
datasets.append(create_polydata_from_pc(*rotate_primitive_cell(
            PrimitiveCell.for_hexagonal_lattice(1., 0.5))))

# orthorhombic lattice in a rotated coor. sys.
datasets.append(create_polydata_from_pc(*rotate_primitive_cell(
            PrimitiveCell.for_orthorhombic_lattice(0.5, 0.8, 1.,))))

# orthorhombic lattice in a rotated coor. sys.
# although the primitive cell has a BravaisLattice.ORTHORHOMBIC attribute
# two of the edges are the same lengths
# so it would be recognised as at tetragonal lattice
datasets.append(create_polydata_from_pc(*rotate_primitive_cell(
            PrimitiveCell.for_orthorhombic_lattice(0.5, 1., 1.,))))

# face_centered_orthorhombic lattice in a rotated coor. sys.
datasets.append(create_polydata_from_pc(*rotate_primitive_cell(
            PrimitiveCell.for_face_centered_orthorhombic_lattice(0.5, 0.6, 1.,))))

# base_centered_orthorhombic lattice in a rotated coor. sys.
datasets.append(create_polydata_from_pc(*rotate_primitive_cell(
            PrimitiveCell.for_base_centered_orthorhombic_lattice(0.5, 0.6, 1.,))))

# body_centered_orthorhombic lattice in a rotated coor. sys.
datasets.append(create_polydata_from_pc(*rotate_primitive_cell(
            PrimitiveCell.for_body_centered_orthorhombic_lattice(0.5, 0.6, 1.,))))

# monoclinic lattice in a rotated coor. sys.
datasets.append(create_polydata_from_pc(*rotate_primitive_cell(
            PrimitiveCell.for_monoclinic_lattice(0.5, 0.6, 1., 0.3))))

# base_centered_monoclinic lattice in a rotated coor. sys.
datasets.append(create_polydata_from_pc(*rotate_primitive_cell(
            PrimitiveCell.for_base_centered_monoclinic_lattice(0.5, 0.6, 1., 0.7))))

# triclinic lattice in a rotated coor. sys.
datasets.append(create_polydata_from_pc(*rotate_primitive_cell(
            PrimitiveCell.for_triclinic_lattice(0.5, 0.6, 1., 0.6, 0.4, 0.8))))


def add_temperature(lattice):
    new_nodes = []
    for node in lattice.iter_nodes():
        index = numpy.array(node.index) + 1.0
        node.data[CUBA.TEMPERATURE] = numpy.prod(index)
        new_nodes.append(node)
    lattice.update_nodes(new_nodes)

# Now view the data.
@mayavi2.standalone
def view(lattice):
    from mayavi.modules.glyph import Glyph
    from simphony_mayavi.sources.api import CUDSSource
    mayavi.new_scene()  # noqa
    src = CUDSSource(cuds=lattice)
    mayavi.add_source(src)  # noqa
    g = Glyph()
    gs = g.glyph.glyph_source
    gs.glyph_source = gs.glyph_dict['sphere_source']
    g.glyph.glyph.scale_factor = 0.2
    g.glyph.scale_mode = 'data_scaling_off'
    mayavi.add_module(g)  # noqa

if __name__ == '__main__':
    for data_set in datasets:
        vtk_lattice = mayavi_tools.VTKLattice.from_dataset("test", data_set)
        print vtk_lattice.primitive_cell.bravais_lattice
