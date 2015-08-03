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

.. image:: https://readthedocs.org/projects/simphony-mayavi/badge/?version=stable
  :target: https://readthedocs.org/projects/simphony-mayavi/?badge=stable
  :alt: Documentation Status

Repository
----------

Simphony-mayavi is hosted on github: https://github.com/simphony/simphony-mayavi

Requirements
------------

- mayavi >= 4.4.0
- simphony >= 0.1.3

Optional requirements
~~~~~~~~~~~~~~~~~~~~~

To support the documentation built you need the following packages:

- sphinx >= 1.2.3
- sectiondoc commit 8a0c2be, https://github.com/enthought/sectiondoc
- trait-documenter, https://github.com/enthought/trait-documenter
- mock

Alternative running :command:`pip install -r doc_requirements` should install the
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

  from simphony.visualization import mayavi_tools
  mayavi_tools.show(cuds)


Directory structure
-------------------


- simphony-mayavi -- Main package folder.

  - sources -- Wrap CUDS objects to provide Mayavi Sources.
  - cuds -- Wrap VTK Dataset objects to provide the CUDS container api.
  - core -- Utility classes and tools to manipulate vtk and cuds objects.
- examples -- Holds examples of loading and visualising SimPhoNy objects with simphony-mayavi.
- doc -- Documentation related files:
  - The rst source files for the documentation
