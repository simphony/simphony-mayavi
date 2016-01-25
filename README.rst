Simphony-Mayavi
===============

A plugin-library for the Simphony framework (http://www.simphony-project.eu/) to provide
visualization support of the CUDS highlevel components.

.. image:: https://travis-ci.org/simphony/simphony-mayavi.svg?branch=master
  :target: https://travis-ci.org/simphony/simphony-mayavi
  :alt: Build status

.. image:: http://codecov.io/github/simphony/simphony-mayavi/coverage.svg?branch=master
  :target: http://codecov.io/github/simphony/simphony-mayavi?branch=master
  :alt: Test coverage

.. image:: https://readthedocs.org/projects/simphony-mayavi/badge/?version=latest
  :target: https://readthedocs.org/projects/simphony-mayavi/?badge=latest
  :alt: Documentation Status

Repository
----------

Simphony-mayavi is hosted on github: https://github.com/simphony/simphony-mayavi

Requirements
------------

- mayavi[app] >= 4.4.0
- simphony[H5IO] >= 0.3.0

Optional requirements
~~~~~~~~~~~~~~~~~~~~~

To support testing, you will need the following packages:

- PIL
- mock

Alternatively unning :command:`pip install -r dev-requirements.txt` should install the
packages needed for development purposes.


To support the documentation built you need the following packages:

- sphinx >= 1.2.3
- sectiondoc commit 8a0c2be, https://github.com/enthought/sectiondoc
- trait-documenter, https://github.com/enthought/trait-documenter

Alternative running :command:`pip install -r doc_requirements.txt` should install the
minimum necessary components for the documentation built.

Installation
------------

The package requires python 2.7.x, installation is based on setuptools::

  # build and install
  python setup.py install

or::

  # build for in-place development
  python setup.py develop

Testing
-------

To run the full test-suite run::

  python -m unittest discover

Documentation
-------------

To build the documentation in the doc/build directory run::

  python setup.py build_sphinx

.. note::

  - One can use the --help option with a setup.py command
    to see all available options.
  - The documentation will be saved in the ``./build`` directory.

Usage
-----

After installation the user should be able to import the ``mayavi`` visualization plugin module by::

  from simphony.visualisation import mayavi_tools
  mayavi_tools.show(cuds)

.. note::

   - It is also recommended that the user uses qt4 as the user interface backends by setting the
     environment variable ``ETS_TOOLKIT``.  In Bash, that is::

       export ETS_TOOLKIT=qt4


Known Issues
------------

- *Segmentation fault during loading or running test suites*

  This may be caused by installing BOTH simphony-paraview_ and simphony-mayavi in the same environment.
  Since paraview and mayavi use different versions of VTK, work-around is limited.  Here are two possible
  solutions.
  
  - If you don't need both simphony-mayavi and simphony-paraview, uninstall one of them, e.g.::
  
      pip uninstall simphony-paraview
  
  - If you must retain both plugins, choose to remove one of them from the ``simphony.visualisation`` entry points.
    The plugin removed from ``simphony.visualisation`` is still accessible via ``import simphony_paraview.plugin`` or ``import simphony_mayavi.plugin``.  Notice that this change would cause plugin loading tests to fail.
  
  
.. _simphony-paraview: http://github.com/simphony/simphony-paraview

Directory structure
-------------------

- simphony-mayavi -- Main package folder.

  - sources -- Wrap CUDS objects to provide Mayavi Sources.
  - cuds -- Wrap VTK Dataset objects to provide the CUDS container api.
  - core -- Utility classes and tools to manipulate vtk and cuds objects.
- examples -- Holds examples of loading and visualising SimPhoNy objects with simphony-mayavi.
- doc -- Documentation related files:
  - The rst source files for the documentation
