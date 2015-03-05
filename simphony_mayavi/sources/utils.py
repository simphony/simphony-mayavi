def cell_array_slicer(data):
    """ Iterate over cell components on a vtk cell array

    VTK stores the associated point index for each cell in a one
    dimensional array based on the following template::

      [n, id0, id1, id2, ..., idn, m, id0, ...]

    The iterator takes a cell array and returns the point indices for
    each cell.

    """
    count = 0
    collection = []
    for value in data:
        if count == 0:
            collection = []
            count = value
        else:
            collection.append(value)
            count -= 1
            if count == 0:
                yield collection
