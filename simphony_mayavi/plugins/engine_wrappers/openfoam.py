from simphony.engine import openfoam_file_io
from simphony.engine import openfoam_internal


def get_foam_internal_wrapper():
    ''' Return an OpenFoam Wrapper using Internal interface '''
    return openfoam_internal.FoamInternalWrapper()


def get_foam_file_io_wrapper():
    ''' Return an OpenFoam Wrapper using File-IO interface '''
    return openfoam_file_io.FoamControlWrapper()


def get_factories():
    ''' Return a dictionary containing the factory functions
    for creating engine wrappers.

    Returns
    -------
    factories : dict
        {"name of the factory": callable}
    '''
    return {"OpenFoam File/IO": get_foam_file_io_wrapper,
            "OpenFoam Internal": get_foam_internal_wrapper}
