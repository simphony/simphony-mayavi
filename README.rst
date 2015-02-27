Simphony-Mayavi
===============

A plugin-library for the Simphony framework to provide visualization support of the CUDS highlevel components

.. image:: https://travis-ci.org/simphony/simphony-mayavi.svg?branch=master
  :target: https://travis-ci.org/simphony/simphony-mayavi
  :alt: Build status

.. image:: https://coveralls.io/repos/simphony/simphony-mayavi/badge.svg
  :target: https://coveralls.io/r/simphony/simphony-mayavi
  :alt: Test coverage

.. image:: https://readthedocs.org/projects/simphony-mayavi/badge/?version=master
  :target: https://readthedocs.org/projects/simphony-mayavi/?badge=master
  :alt: Documentation Status

Repository
----------

Simphony-mayavi is hosted on github: https://github.com/simphony/simphony-mayavi

Requirements
------------

- mayavi >= 4.4.0
- simphony >= 0.0.1

Optional requirements
~~~~~~~~~~~~~~~~~~~~~

To support the documentation built you need the following packages:

- sphinx >= 1.2.3
- sphinxcontrib-napoleon >= 0.2.10
- mock

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

  from simphony.visualization import mayavi
  mayavi.show(cuds)


Directory structure
-------------------

There are four subpackages:

- simphony-mayavi -- Main package code.
- examples -- Holds examples of visualizing simphony objects with simphony-mayavi.
- doc -- Documentation related files:

  - source -- Sphinx rst source files
  - build -- Documentation build directory, if documentation has been generated
    using the ``make`` script in the ``doc`` directory.


