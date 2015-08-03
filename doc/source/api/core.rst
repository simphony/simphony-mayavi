Core module
===========

A module containing core tools and wrappers for vtk data containers
used in simphony_mayavi.

.. rubric:: Classes

.. currentmodule:: simphony_mayavi.core

.. autosummary::

    ~cuba_data.CubaData
    ~cell_collection.CellCollection
    ~doc_utils.mergedocs
    ~cuba_data_accumulator.CUBADataAccumulator
    ~cuba_data_extractor.CUBADataExtractor

.. rubric:: Functions

.. autosummary::

   ~cuba_utils.supported_cuba
   ~cuba_utils.default_cuba_value
   ~cell_array_tools.cell_array_slicer
   ~doc_utils.mergedoc


Description
-----------

.. autoclass:: simphony_mayavi.core.cuba_data.CubaData
     :members:
     :undoc-members:
     :show-inheritance:

.. autoclass:: simphony_mayavi.core.cell_collection.CellCollection
     :members: insert, __delitem__, __getitem__, __setitem__, __len__
     :undoc-members:
     :show-inheritance:

.. autoclass:: simphony_mayavi.core.cuba_data_accumulator.CUBADataAccumulator
     :members:
     :special-members: __getitem__, __len__
     :undoc-members:
     :show-inheritance:

.. autoclass:: simphony_mayavi.core.cuba_data_extractor.CUBADataExtractor
     :members:
     :undoc-members:
     :show-inheritance:

.. autoclass:: simphony_mayavi.core.doc_utils.mergedocs
     :members:
     :undoc-members:
     :show-inheritance:

.. autofunction:: simphony_mayavi.core.cuba_utils.supported_cuba

.. autofunction:: simphony_mayavi.core.cuba_utils.default_cuba_value

.. autofunction:: simphony_mayavi.core.cell_array_tools.cell_array_slicer

.. autofunction:: simphony_mayavi.core.doc_utils.mergedoc
