import sys

from mayavi import mlab
from contextlib import contextmanager

from simphony.cuds.abc_mesh import ABCMesh
from simphony.cuds.abc_particles import ABCParticles
from simphony.cuds.abc_lattice import ABCLattice

from simphony_mayavi.sources.api import CUDSSource
from simphony_mayavi.modules.default_module import default_module


@contextmanager
def get_figure(*args, **kwargs):
    old_option = mlab.options.offscreen
    try:
        # offscreen on Windows works reliably
        if sys.platform == "win32":
            mlab.options.offscreen = True

        # Make sure a new figure is created
        figure = mlab.figure(*args, **kwargs)
        # if offscreen is True, this is set already
        figure.scene.off_screen_rendering = True

        yield figure

    finally:
        mlab.options.offscreen = old_option
        mlab.clf()
        mlab.close()


def snapshot(cuds, filename):
    """ Save a snapshot of the cuds object using the default visualisation.

     Parameters
     ----------
     cuds :
         A top level cuds object (e.g. a mesh). The method will detect
         the type of object and create the appropriate visualisation.

     filename : string
         The filename to use for the output file.

    """
    # adapt to CUDSSource
    if isinstance(cuds, (ABCMesh, ABCParticles, ABCLattice)):
        source = CUDSSource(cuds=cuds)
    else:
        msg = 'Provided object {} is not of any known cuds type'
        raise TypeError(msg.format(type(cuds)))

    # set image size
    size = 800, 600

    with get_figure(size=size):
        # add source
        mlab.pipeline.add_dataset(source)

        modules = default_module(source)

        # add default modules
        for module in modules:
            source.add_module(module)

        mlab.savefig(filename, size=size)
