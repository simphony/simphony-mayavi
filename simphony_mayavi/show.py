from simphony.cuds.abstractmesh import ABCMesh
from simphony.cuds.abstractparticles import ABCParticles


def show(cuds):

    if isinstance(cuds, ABCMesh):
        raise NotImplementedError()
    elif isinstance(cuds, ABCParticles):
        raise NotImplementedError()
    else:
        msg = 'Provided object {} is not of any known cuds type'
        raise TypeError(msg.format(type(cuds)))
