from simphony.engine import kratos


def get_cdf_wrapper():
    ''' Return a Kratos CDF Wrapper '''
    return kratos.CFDWrapper()


def get_dem_wrapper():
    ''' Return a Kratos DEM wrapper '''
    return kratos.DEMWrapper()


def get_factories():
    ''' Return a dictionary containing the factory functions
    for creating engine wrappers.

    Returns
    -------
    factories : dict
        {"name of the factory": callable}
    '''
    return {"Kratos-CFD": get_cdf_wrapper,
            "Kratos-DEM": get_dem_wrapper}
