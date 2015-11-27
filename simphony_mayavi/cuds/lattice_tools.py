from itertools import permutations, combinations

import numpy
from simphony.cuds.primitive_cell import PrimitiveCell, BravaisLattice


def vector_len(vec):
    ''' Length of vector

    Parameter
    ---------
    vec : array_like

    Returns
    -------
    length : ndarray
    '''
    return numpy.sqrt(numpy.dot(vec, vec))


def cosine_two_vectors(vec1, vec2):
    ''' Return the cosine of the acute angle between two vectors

    Parameters
    ----------
    vec1 : array_like
    vec2 : array_like


    Returns
    -------
    cosine : numpy ndarray
    '''
    vec1_length = vector_len(vec1)
    vec2_length = vector_len(vec2)
    return numpy.dot(vec1, vec2)/vec1_length/vec2_length


def same_lattice_type(target_pc, p1, p2, p3):
    ''' Return True if a set of primitive vectors ``p1``, ``p2``,
    ``p3`` describes the same type of lattice as the target
    primitive cell ``target_pc`` does.  Single precision applies.

    Parameters
    ----------
    target_pc : PrimitiveCell
    p1 : array_like (len=3)
    p2 : array_like (len=3)
    p3 : array_like (len=3)

    Returns
    -------
    match : bool
    '''
    pcs = (target_pc.p1, target_pc.p2, target_pc.p3)

    # cosine angles between pairs of the target primitive vectors
    target_cosines = tuple(cosine_two_vectors(vec1, vec2)
                           for vec1, vec2 in combinations(pcs, 2))

    # length ratios between pairs of the target primitive vectors
    target_ratios = tuple(vector_len(vec1)/vector_len(vec2)
                          for vec1, vec2 in permutations(pcs, 2))

    for iperm, perms in enumerate(permutations((p1, p2, p3), 3)):
        cosines = tuple(cosine_two_vectors(vec1, vec2)
                        for vec1, vec2 in combinations(perms, 2))
        ratios = tuple(vector_len(vec1)/vector_len(vec2)
                       for vec1, vec2 in permutations(perms, 2))

        # single precision
        atol = numpy.finfo(numpy.float32).resolution
        if (numpy.allclose(cosines, target_cosines, atol=atol) and
                numpy.allclose(ratios, target_ratios, atol=atol)):
            return True
    return False


def guess_primitive_vectors(points):
    ''' Guess the primitive vectors underlying a given array of
    lattice points (N, 3).

    Assume the points are arranged in C-contiguous order so that
    the first point is the origin, the last point is furthest away
    from the origin

    Parameter
    ----------
    points : numpy ndarray (N, 3)
        intended for tvtk.PolyData.points.to_array()

    Returns
    -------
    p1, p2, p3 : 3 x tuple of float[3]
        primitive vectors
    '''
    def find_jump(arr1d):
        ''' Return the index where the first derivation changes '''
        sec_dev = numpy.diff(arr1d, n=2)
        return numpy.where(~numpy.isclose(sec_dev, 0.))[0][0]+2

    for idim in range(3):
        try:
            nx = find_jump(points[:, idim])
            break
        except IndexError:   # numpy.where is empty
            continue
    else:
        message = "Failed to deduce the first lattice dimension"
        raise IndexError(message)

    for idim in range(3):
        try:
            ny = find_jump(points[::nx, idim])
            break
        except IndexError:   # numpy.where is empty
            continue
    else:
        message = "Failed to deduce the second lattice dimension"
        raise IndexError(message)

    # Test if the lattice points are ordered as expected
    if not (numpy.allclose(numpy.diff(points[:nx, 0], n=2), 0.) and
            numpy.allclose(numpy.diff(points[::nx, 1][:ny], n=2), 0.) and
            numpy.allclose(numpy.diff(points[::nx*ny, 2], n=2), 0.)):
        message = ("Deduction of the primitive vectors requires the "
                   "lattice nodes to be ordered in a C-contiguous fashion.")
        raise IndexError(message)

    # Primitive vectors
    return tuple((points[ipoint, 0]-points[0, 0],
                  points[ipoint, 1]-points[0, 1],
                  points[ipoint, 2]-points[0, 2]) for ipoint in (1, nx, nx*ny))


def is_cubic_lattice(p1, p2, p3):
    ''' Test if primitive vectors describe a cubic lattice

    Parameters
    ----------
    p1, p2, p3: array_like
        primitive vectors

    Returns
    -------
    output : bool
    '''
    # single precision
    vec_lengths = numpy.array(map(vector_len, (p1, p2, p3)),
                              dtype=numpy.float32)
    unique_lengths = numpy.unique(vec_lengths)

    if len(unique_lengths) != 1:
        return False

    return same_lattice_type(PrimitiveCell.for_cubic_lattice(1.), p1, p2, p3)


def is_body_centered_cubic_lattice(p1, p2, p3):
    ''' Test if primitive vectors describe a body centered cubic lattice

    Parameters
    ----------
    p1, p2, p3: array_like
        primitive vectors

    Returns
    -------
    output : bool
    '''
    # single precision
    vec_lengths = numpy.array(map(vector_len, (p1, p2, p3)),
                              dtype=numpy.float32)
    unique_lengths = numpy.unique(vec_lengths)

    if len(unique_lengths) != 2:
        return False

    return same_lattice_type(PrimitiveCell.for_body_centered_cubic_lattice(1.),
                             p1, p2, p3)


def is_face_centered_cubic_lattice(p1, p2, p3):
    ''' Test if primitive vectors describe a face centered cubic lattice

    Parameters
    ----------
    p1, p2, p3: array_like
        primitive vectors

    Returns
    -------
    output : bool
    '''
    # single precision
    vec_lengths = numpy.array(map(vector_len, (p1, p2, p3)),
                              dtype=numpy.float32)
    unique_lengths = numpy.unique(vec_lengths)

    if len(unique_lengths) != 1:
        return False

    return same_lattice_type(PrimitiveCell.for_face_centered_cubic_lattice(1.),
                             p1, p2, p3)


def is_rhombohedral_lattice(p1, p2, p3):
    ''' Test if primitive vectors describe a rhombohedral lattice

    Also returns True for vectors describing a cubic lattice

    Parameters
    ----------
    p1, p2, p3: array_like
        primitive vectors

    Returns
    -------
    output : bool
    '''
    # single precision
    vec_lengths = numpy.array(map(vector_len, (p1, p2, p3)),
                              dtype=numpy.float32)
    unique_lengths = numpy.unique(vec_lengths)

    if len(unique_lengths) != 1:
        return False

    beta = numpy.arccos(cosine_two_vectors(p1, p2))
    angle1 = beta % numpy.pi

    if numpy.allclose(angle1, 0) or numpy.allclose(angle1, numpy.pi):
        return False

    return same_lattice_type(PrimitiveCell.for_rhombohedral_lattice(1., beta),
                             p1, p2, p3)


def is_tetragonal_lattice(p1, p2, p3):
    ''' Test if primitive vectors describe a tetragonal lattice

    Also returns True for vectors describing a cubic lattice

    Parameters
    ----------
    p1, p2, p3: array_like
        primitive vectors

    Returns
    -------
    output : bool
    '''
    # single precision
    vec_lengths = numpy.array(map(vector_len, (p1, p2, p3)),
                              dtype=numpy.float32)
    unique_lengths = numpy.unique(vec_lengths)

    if len(unique_lengths) > 2:
        return False
    elif len(unique_lengths) == 1:
        common = other = unique_lengths[0]
    elif sum((vec_len == unique_lengths[0] for vec_len in vec_lengths)) == 2:
        common, other = unique_lengths
    else:
        other, common = unique_lengths

    target_pc = PrimitiveCell.for_tetragonal_lattice(common, other)
    return same_lattice_type(target_pc, p1, p2, p3)


def is_body_centered_tetragonal_lattice(p1, p2, p3):
    ''' Test if primitive vectors describe a body centered tetragonal
    lattice

    Also returns True for vectors describing a body centered cubic
    lattice

    Parameters
    ----------
    p1, p2, p3: array_like
        primitive vectors

    Returns
    -------
    output : bool
    '''
    # single precision
    vec_lengths = numpy.array(map(vector_len, (p1, p2, p3)),
                              dtype=numpy.float32)
    unique_lengths = numpy.unique(vec_lengths)

    if len(unique_lengths) != 2:
        return False

    factory = PrimitiveCell.for_body_centered_tetragonal_lattice

    for alpha, gamma in permutations(unique_lengths, 2):
        delta = gamma**2. - 0.5*alpha**2.
        if (delta > 0. and
                same_lattice_type(factory(alpha, 2.*numpy.sqrt(delta)),
                                  p1, p2, p3)):
            return True
    return False


def is_hexagonal_lattice(p1, p2, p3):
    ''' Test if primitive vectors describe a hexagonal lattice

    Parameters
    ----------
    p1, p2, p3: array_like
        primitive vectors

    Returns
    -------
    output : bool
    '''
    # single precision
    vec_lengths = numpy.array(map(vector_len, (p1, p2, p3)),
                              dtype=numpy.float32)
    unique_lengths = numpy.unique(vec_lengths)

    factory = PrimitiveCell.for_hexagonal_lattice

    if len(unique_lengths) == 3:
        return False
    elif len(unique_lengths) == 1:
        return same_lattice_type(factory(1., 1.), p1, p2, p3)
    else:
        if sum((vec_len == unique_lengths[0] for vec_len in vec_lengths)) == 2:
            common, other = unique_lengths
        else:
            other, common = unique_lengths

        target_pc = factory(common, other)
        return same_lattice_type(target_pc, p1, p2, p3)


def is_orthorhombic_lattice(p1, p2, p3):
    ''' Test if primitive vectors describe an orthorhombic lattice

    Also returns True for vectors describing a cubic or tetragonal
    lattice

    Parameters
    ----------
    p1, p2, p3: array_like
        primitive vectors

    Returns
    -------
    output : bool
    '''
    vec_lengths = map(vector_len, (p1, p2, p3))
    factory = PrimitiveCell.for_orthorhombic_lattice
    return same_lattice_type(factory(*vec_lengths), p1, p2, p3)


def is_body_centered_orthorhombic_lattice(p1, p2, p3):
    ''' Test if primitive vectors describe a body centered orthorhombic
    lattice

    Also returns True for vectors describing a body centered cubic or
    a body centered tetragonal lattice

    Parameters
    ----------
    p1, p2, p3: array_like
        primitive vectors

    Returns
    -------
    output : bool
    '''
    vec_lengths = map(vector_len, (p1, p2, p3))
    factory = PrimitiveCell.for_body_centered_orthorhombic_lattice

    for alpha, beta, gamma in permutations(vec_lengths):
        delta = 4*gamma**2.-alpha**2.-beta**2.
        if (delta > 0. and
                same_lattice_type(factory(alpha, beta, numpy.sqrt(delta)),
                                  p1, p2, p3)):
            return True
    return False


def is_face_centered_orthorhombic_lattice(p1, p2, p3):
    ''' Test if primitive vectors describe a face centered orthorhombic
    lattice

    Also returns True for vectors describing a face centered cubic
    lattice

    Parameters
    ----------
    p1, p2, p3: array_like
        primitive vectors

    Returns
    -------
    output : bool
    '''
    vec_lengths = map(vector_len, (p1, p2, p3))
    factory = PrimitiveCell.for_face_centered_orthorhombic_lattice

    alpha, beta, gamma = vec_lengths
    a2 = 2.*(gamma**2.+beta**2.-alpha**2.)
    b2 = 2.*(alpha**2.+gamma**2.-beta**2.)
    c2 = 2.*(alpha**2.+beta**2.-gamma**2.)

    if a2 <= 0 or b2 <= 0 or c2 <= 0:
        return False

    for abc in permutations(map(numpy.sqrt, (a2, b2, c2)), 3):
        if same_lattice_type(factory(*abc), p1, p2, p3):
            return True
    return False


def is_base_centered_orthorhombic_lattice(p1, p2, p3):
    ''' Test if primitive vectors describe a base centered orthorhombic
    lattice

    Parameters
    ----------
    p1, p2, p3: array_like
        primitive vectors

    Returns
    -------
    output : bool
    '''
    vec_lengths = map(vector_len, (p1, p2, p3))
    factory = PrimitiveCell.for_base_centered_orthorhombic_lattice

    for alpha, beta, gamma in permutations(vec_lengths, 3):
        delta = 4.*beta**2.-alpha**2.
        if (delta > 0. and
                same_lattice_type(factory(alpha, numpy.sqrt(delta), gamma),
                                  p1, p2, p3)):
            return True
    return False


def is_monoclinic_lattice(p1, p2, p3):
    ''' Test if primitive vectors describe a monoclinic lattice

    Also returns True for vectors describing a cubic, an orthorhombic
    or a base centered orthorhombic lattice

    Parameters
    ----------
    p1, p2, p3: array_like
        primitive vectors

    Returns
    -------
    output : bool
    '''
    alpha, beta, gamma = map(vector_len, (p1, p2, p3))
    factory = PrimitiveCell.for_monoclinic_lattice

    theta = numpy.arcsin(numpy.clip(numpy.dot(numpy.cross(p1, p2),
                                              p3)/alpha/beta/gamma, -1., 1.))
    angle1 = theta % numpy.pi

    if numpy.allclose(angle1, 0.) or numpy.allclose(angle1, numpy.pi):
        return False

    for edges in permutations((alpha, beta, gamma), 3):
        if same_lattice_type(factory(*(edges+(theta,))), p1, p2, p3):
            return True
    return False


def is_base_centered_monoclinic_lattice(p1, p2, p3):
    ''' Test if primitive vectors describe a base centered monoclinic
    lattice

    Also returns True for vectors describing a base centered
    orthorhombic lattice or a monoclinic lattice

    Parameters
    ----------
    p1, p2, p3: array_like
        primitive vectors

    Returns
    -------
    output : bool
    '''
    vec_lengths = map(vector_len, (p1, p2, p3))
    factory = PrimitiveCell.for_base_centered_monoclinic_lattice

    for alpha, beta, gamma in permutations(vec_lengths, 3):
        delta = 4.*beta**2.-alpha**2.
        if delta <= 0.:
            continue
        sin_theta = numpy.dot(numpy.cross(p1, p2),
                              p3)/alpha/numpy.sqrt(delta)/gamma*2.
        theta = numpy.arcsin(numpy.clip(sin_theta, -1., 1.))
        angle1 = theta % numpy.pi
        if (not numpy.isclose(angle1, 0.) and
                not numpy.isclose(angle1, numpy.pi) and
                same_lattice_type(factory(alpha, numpy.sqrt(delta),
                                          gamma, theta),
                                  p1, p2, p3)):
            return True
    return False


def is_triclinic_lattice(p1, p2, p3):
    ''' Test if primitive vectors describe a triclinic lattice

    Also returns True for vectors describing any other types of Bravais
    lattices

    Parameters
    ----------
    p1, p2, p3: array_like
        primitive vectors

    Returns
    -------
    output : bool
    '''
    edges = tuple(map(vector_len, (p1, p2, p3)))
    factory = PrimitiveCell.for_triclinic_lattice

    alpha, beta, gamma = (numpy.arccos(cosine_two_vectors(p2, p3)),
                          numpy.arccos(cosine_two_vectors(p1, p3)),
                          numpy.arccos(cosine_two_vectors(p1, p2)))
    a1 = alpha % numpy.pi
    a2 = beta % numpy.pi
    a3 = gamma % numpy.pi

    if (numpy.any(numpy.isclose((a1, a2, a3), (0,)*3)) or
            numpy.any(numpy.isclose((a1, a2, a3), (numpy.pi,)*3))):
        return False

    return (numpy.all(numpy.greater((a1+a2, a1+a3, a2+a3), (a3, a2, a1))) and
            same_lattice_type(factory(*(edges+(alpha, beta, gamma))),
                              p1, p2, p3))


def find_lattice_type(p1, p2, p3):
    ''' Return the lattice type as BravaisLattice(IntEnum)
    given a set of primitive vectors

    Parameters
    ----------
    p1, p2, p3 : 3 x float[3]
        primitive vectors

    Returns
    -------
    BravaisLattice(IntEnum)

    Raises
    ------
    TypeError
        if none of the predefined BravaisLattice matches
        the given primitive vectors
    '''
    # Should be ordered from the most specific lattice
    # to the most general ones
    if is_cubic_lattice(p1, p2, p3):
        return BravaisLattice.CUBIC
    elif is_body_centered_cubic_lattice(p1, p2, p3):
        return BravaisLattice.BODY_CENTERED_CUBIC
    elif is_face_centered_cubic_lattice(p1, p2, p3):
        return BravaisLattice.FACE_CENTERED_CUBIC
    elif is_rhombohedral_lattice(p1, p2, p3):
        return BravaisLattice.RHOMBOHEDRAL
    elif is_tetragonal_lattice(p1, p2, p3):
        return BravaisLattice.TETRAGONAL
    elif is_body_centered_tetragonal_lattice(p1, p2, p3):
        return BravaisLattice.BODY_CENTERED_TETRAGONAL
    elif is_hexagonal_lattice(p1, p2, p3):
        return BravaisLattice.HEXAGONAL
    elif is_orthorhombic_lattice(p1, p2, p3):
        return BravaisLattice.ORTHORHOMBIC
    elif is_body_centered_orthorhombic_lattice(p1, p2, p3):
        return BravaisLattice.BODY_CENTERED_ORTHORHOMBIC
    elif is_face_centered_orthorhombic_lattice(p1, p2, p3):
        return BravaisLattice.FACE_CENTERED_ORTHORHOMBIC
    elif is_base_centered_orthorhombic_lattice(p1, p2, p3):
        return BravaisLattice.BASE_CENTERED_ORTHORHOMBIC
    elif is_monoclinic_lattice(p1, p2, p3):
        return BravaisLattice.MONOCLINIC
    elif is_base_centered_monoclinic_lattice(p1, p2, p3):
        return BravaisLattice.BASE_CENTERED_MONOCLINIC
    elif is_triclinic_lattice(p1, p2, p3):
        return BravaisLattice.TRICLINIC
    else:
        message = ("None of the predefined Bravais Lattices matches the "
                   "given primitive vectors")
        raise TypeError(message)
