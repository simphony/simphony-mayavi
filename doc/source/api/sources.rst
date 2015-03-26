Sources module
==============

A module containing tools to convert from CUDS containers to Mayavi
compatible sources. Please use the ``simphony_mayavi.sources.api``
module to access the provided tools.

.. rubric:: Classes

.. currentmodule:: simphony_mayavi.sources

.. autosummary::

    ~particles_source.ParticlesSource
    ~lattice_source.LatticeSource
    ~mesh_source.MeshSource
    ~cuds_data_accumulator.CUDSDataAccumulator
    ~cuds_data_extractor.CUDSDataExtractor

.. rubric:: Functions

.. autosummary::

   ~utils.cell_array_slicer

.. rubric:: Implementation

-----

.. autoclass:: simphony_mayavi.sources.particles_source.ParticlesSource
     :members:
     :undoc-members:
     :show-inheritance:

.. autoclass:: simphony_mayavi.sources.mesh_source.MeshSource
     :members:
     :undoc-members:
     :show-inheritance:

.. autoclass:: simphony_mayavi.sources.lattice_source.LatticeSource
     :members:
     :undoc-members:
     :show-inheritance:

.. autoclass:: simphony_mayavi.sources.cuds_data_accumulator.CUDSDataAccumulator
     :members:
     :special-members: __getitem__, __len__
     :undoc-members:
     :show-inheritance:

.. autoclass:: simphony_mayavi.sources.cuds_data_extractor.CUDSDataExtractor
     :members:
     :undoc-members:
     :show-inheritance:

.. autofunction:: simphony_mayavi.sources.utils.cell_array_slicer
