from simphony.engine import lammps


def get_lammps_file_io_wrapper():
    ''' Return a LammpsWrapper using File-IO interface '''
    return lammps.LammpsWrapper(use_internal_interface=False)


def get_lammps_internal_wrapper():
    ''' Return a LammpsWrapper using Internal interface '''
    return lammps.LammpsWrapper(use_internal_interface=True)


def get_factories():
    ''' Return a dictionary containing the factory functions
    for creating engine wrappers.

    Returns
    -------
    factories : dict
        {"name of the factory": callable}
    '''
    return {"Lammps File/IO": get_lammps_file_io_wrapper,
            "Lammps Internal": get_lammps_internal_wrapper}
