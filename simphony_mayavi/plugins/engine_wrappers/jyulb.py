from simphony.engine import jyulb_fileio_isothermal, jyulb_internal_isothermal


def get_jyulb_fileio_wrapper():
    ''' Return a JYU-LB Wrapper using Fil-IO interface '''
    return jyulb_fileio_isothermal.JYULBEngine()


def get_jyulb_internal_wrapper():
    ''' Return a JYU-LB Wrapper using Internal interface '''
    return jyulb_internal_isothermal.JYULBEngine()


def get_factories():
    ''' Return a dictionary containing the factory functions
    for creating engine wrappers.

    Returns
    -------
    factories : dict
        {"name of the factory": callable}
    '''
    return {"JYULB File/IO": get_jyulb_fileio_wrapper,
            "JYULB Internal": get_jyulb_internal_wrapper}
