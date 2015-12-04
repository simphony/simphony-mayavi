import unittest

import numpy
from hypothesis import given
from hypothesis.strategies import floats, tuples, composite
from hypothesis.strategies import fixed_dictionaries

from simphony.cuds.primitive_cell import BravaisLattice, PrimitiveCell
import simphony_mayavi.cuds.lattice_tools as lattice_tools


# Tests for Error raised by PrimitiveCell should be placed separately
# Edge lengths and angles are assumed to be valid
edges = floats(min_value=0.1, max_value=1.).filter(lambda x: x == x)
angles = floats(min_value=0.1, max_value=numpy.pi-0.1).filter(lambda x: x == x)


@composite
def builds_unpack(draw, factory, elements):
    ''' Similar to hypothesis.strategies.builds except
    it unpacks the arguments '''
    args = elements.example()
    return factory(*args)

# define how primitive cell should be built
factories = {
    BravaisLattice.CUBIC:
        (PrimitiveCell.for_cubic_lattice, tuples(edges)),
    BravaisLattice.BODY_CENTERED_CUBIC:
        (PrimitiveCell.for_body_centered_cubic_lattice, tuples(edges)),
    BravaisLattice.FACE_CENTERED_CUBIC:
        (PrimitiveCell.for_face_centered_cubic_lattice, tuples(edges)),
    BravaisLattice.RHOMBOHEDRAL:
        (PrimitiveCell.for_rhombohedral_lattice, tuples(edges, angles)),
    BravaisLattice.TETRAGONAL:
        (PrimitiveCell.for_tetragonal_lattice, tuples(edges, edges)),
    BravaisLattice.BODY_CENTERED_TETRAGONAL:
        (PrimitiveCell.for_body_centered_tetragonal_lattice,
         tuples(edges, edges)),
    BravaisLattice.HEXAGONAL:
        (PrimitiveCell.for_hexagonal_lattice, tuples(edges, edges)),
    BravaisLattice.ORTHORHOMBIC:
        (PrimitiveCell.for_orthorhombic_lattice,
         tuples(edges, edges, edges)),
    BravaisLattice.BODY_CENTERED_ORTHORHOMBIC:
        (PrimitiveCell.for_body_centered_orthorhombic_lattice,
         tuples(edges, edges, edges)),
    BravaisLattice.FACE_CENTERED_ORTHORHOMBIC:
        (PrimitiveCell.for_face_centered_orthorhombic_lattice,
         tuples(edges, edges, edges)),
    BravaisLattice.BASE_CENTERED_ORTHORHOMBIC:
        (PrimitiveCell.for_base_centered_orthorhombic_lattice,
         tuples(edges, edges, edges)),
    BravaisLattice.MONOCLINIC:
        (PrimitiveCell.for_monoclinic_lattice,
         tuples(edges, edges, edges, angles)),
    BravaisLattice.BASE_CENTERED_MONOCLINIC:
        (PrimitiveCell.for_base_centered_monoclinic_lattice,
         tuples(edges, edges, edges, angles)),
    BravaisLattice.TRICLINIC:
        (PrimitiveCell.for_triclinic_lattice,
         tuples(edges, edges, edges, angles, angles, angles)),
    }


def for_rhombohedral(a, alpha):
    ''' criteria for a rhombohedral lattice '''
    return (numpy.abs(alpha) < (numpy.pi/3.*2.) and
            not numpy.isclose(alpha, numpy.pi/2.))


def for_triclinic(a, b, c, alpha, beta, gamma):
    ''' criteria for a triclinic lattice '''
    a1, a2, a3 = numpy.mod((alpha, beta, gamma), numpy.pi)
    cosa, cosb, cosg = numpy.cos((alpha, beta, gamma))
    sinb, sing = numpy.sin((beta, gamma))

    return (numpy.all(numpy.greater((a1+a2, a1+a3, a2+a3), (a3, a2, a1))) and
            (sinb**2 - ((cosa-cosb*cosg) / sing)**2) > 0. and
            not numpy.isclose((alpha, beta, alpha),
                              (gamma, gamma, beta)).any())


""" Specific criteria for primitive cell parameters such that
the generated cell's bravais lattice type is the most specific
possible """
criteria = {}
criteria[BravaisLattice.RHOMBOHEDRAL] = for_rhombohedral

criteria[BravaisLattice.TETRAGONAL] = lambda a, c: not numpy.isclose(a, c)

criteria[BravaisLattice.BODY_CENTERED_TETRAGONAL] = (
    lambda a, c: not numpy.isclose(a, c))

criteria[BravaisLattice.ORTHORHOMBIC] = (
    lambda a, b, c: not numpy.isclose((a, b, a), (c, c, b)).any())

criteria[BravaisLattice.BODY_CENTERED_ORTHORHOMBIC] = (
    criteria[BravaisLattice.ORTHORHOMBIC])

criteria[BravaisLattice.FACE_CENTERED_ORTHORHOMBIC] = (
    criteria[BravaisLattice.ORTHORHOMBIC])

criteria[BravaisLattice.BASE_CENTERED_ORTHORHOMBIC] = (
    lambda a, b, c: not numpy.isclose(3.*a**2., b**2.))

criteria[BravaisLattice.MONOCLINIC] = (
    lambda a, b, c, alpha: (not numpy.isclose(alpha, numpy.pi/2.) and
                            not (numpy.isclose(alpha, numpy.pi/3.) and
                                 numpy.isclose((a, b, a), (c, c, b)).any())))

criteria[BravaisLattice.BASE_CENTERED_MONOCLINIC] = (
    criteria[BravaisLattice.MONOCLINIC])

criteria[BravaisLattice.TRICLINIC] = for_triclinic


def filter_func(bravais_lattice):
    def new_func(args):
        if bravais_lattice in criteria:
            return criteria[bravais_lattice](*args)
        return True
    return new_func


def builder(bravais_lattices=None):
    lattices = {}
    if bravais_lattices is None:
        bravais_lattices = factories.keys()

    for bravais_lattice in bravais_lattices:
        factory, elements = factories[bravais_lattice]
        filtered = elements.filter(filter_func(bravais_lattice))
        lattices[bravais_lattice] = builds_unpack(factory, filtered)

    return fixed_dictionaries(lattices)


# A list of general lattices and their special cases
# e.g. cubic and face-centered-cubic are special cases
# of the rhombohedral lattice
ambiguous_lattices = {
    BravaisLattice.RHOMBOHEDRAL: (
        BravaisLattice.CUBIC,
        BravaisLattice.FACE_CENTERED_CUBIC),
    BravaisLattice.TETRAGONAL: (
        BravaisLattice.CUBIC,),
    BravaisLattice.BODY_CENTERED_TETRAGONAL: (
        BravaisLattice.BODY_CENTERED_CUBIC,),
    BravaisLattice.ORTHORHOMBIC: (
        BravaisLattice.CUBIC,
        BravaisLattice.TETRAGONAL),
    BravaisLattice.BODY_CENTERED_ORTHORHOMBIC: (
        BravaisLattice.BODY_CENTERED_CUBIC,
        BravaisLattice.BODY_CENTERED_TETRAGONAL),
    BravaisLattice.FACE_CENTERED_ORTHORHOMBIC: (
        BravaisLattice.FACE_CENTERED_CUBIC,),
    BravaisLattice.BASE_CENTERED_ORTHORHOMBIC: (
        BravaisLattice.HEXAGONAL,),
    BravaisLattice.MONOCLINIC: (
        BravaisLattice.CUBIC,
        BravaisLattice.HEXAGONAL,
        BravaisLattice.TETRAGONAL,
        BravaisLattice.ORTHORHOMBIC,
        BravaisLattice.BASE_CENTERED_ORTHORHOMBIC),
    BravaisLattice.BASE_CENTERED_MONOCLINIC: (
        BravaisLattice.HEXAGONAL,
        BravaisLattice.BASE_CENTERED_ORTHORHOMBIC),
    # all lattices are triclinic
    BravaisLattice.TRICLINIC: BravaisLattice,
    }


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
    xyz_rot = numpy.inner(xy_rot, yz_rot)
    return tuple(numpy.inner(xyz_rot, p) for p in (pc.p1, pc.p2, pc.p3))


def create_points_from_pc(p1, p2, p3, size):
    ''' Create a points array given a set of primitive vectors
    and size'''
    y, z, x = numpy.meshgrid(range(size[1]), range(size[2]), range(size[0]))
    points = numpy.zeros(shape=(x.size, 3), dtype='double')
    for idim in range(3):
        points[:, idim] += p1[idim]*x.ravel() +\
            p2[idim]*y.ravel() +\
            p3[idim]*z.ravel()
    return points


# angles for rotating the primitive vectors
rotate_angles = floats(min_value=-numpy.pi+0.1,
                       max_value=numpy.pi-0.1).filter(lambda x: x == x)

all_lattices = builder()


class TestLatticeTools(unittest.TestCase):

    @staticmethod
    def get_primitive_vectors(primitive_cell):
        return primitive_cell.p1, primitive_cell.p2, primitive_cell.p3

    @given(all_lattices, rotate_angles, rotate_angles)
    def test_specific_definition(self, lattice, alpha, beta):
        for bravais_lattice, primitive_cell in lattice.items():
            vectors = rotate_primitive_cell(primitive_cell, alpha, beta)
            lattice_type = lattice_tools.find_lattice_type(*vectors)
            if lattice_type != bravais_lattice:
                print lattice_type, bravais_lattice, vectors
            self.assertEqual(lattice_type, bravais_lattice)

    @given(all_lattices)
    def test_ambiguous_definition(self, lattice):
        for general, specifics in ambiguous_lattices.items():
            for specific in specifics:
                p1, p2, p3 = self.get_primitive_vectors(lattice[specific])
                self.assertTrue(
                    lattice_tools.is_bravais_lattice_consistent(p1, p2, p3,
                                                                general))

    def test_guess_primitive_vectors(self):
        primitive_cell = PrimitiveCell.for_rhombohedral_lattice(0.1, 0.7)
        p1, p2, p3 = self.get_primitive_vectors(primitive_cell)
        points = create_points_from_pc(p1, p2, p3, (4, 5, 6))
        actual = lattice_tools.guess_primitive_vectors(points)
        numpy.testing.assert_allclose((p1, p2, p3), actual)

    def test_exception_guess_vectors_with_unsorted_points(self):
        primitive_cell = PrimitiveCell.for_rhombohedral_lattice(0.1, 0.7)
        p1, p2, p3 = self.get_primitive_vectors(primitive_cell)
        points = create_points_from_pc(p1, p2, p3, (4, 5, 6))
        numpy.random.shuffle(points)

        with self.assertRaises(IndexError):
            lattice_tools.guess_primitive_vectors(points)

    def test_exception_guess_vectors_with_no_first_jump(self):
        points = numpy.zeros((20, 3))
        with self.assertRaises(IndexError):
            lattice_tools.guess_primitive_vectors(points)

    def test_exception_guess_vectors_with_no_second_jump(self):
        points = numpy.zeros((20, 3))
        points[1, 0] = 2

        with self.assertRaises(IndexError):
            lattice_tools.guess_primitive_vectors(points)
