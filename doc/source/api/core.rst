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

.. rubric:: Functions

.. autosummary::

   ~cuba_utils.supported_cuba
   ~cuba_utils.default_cuba_value

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

.. autofunction:: simphony_mayavi.core.cuba_utils.supported_cuba

.. autofunction:: simphony_mayavi.core.cuba_utils.default_cuba_value
