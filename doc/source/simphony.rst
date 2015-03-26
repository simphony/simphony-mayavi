SimPhoNy
========


Mayavi tools are available in from the simphony library through the
visualisation plugin entry point ``mayavi_tools``::

  from simphony.visualisation import mayavi_tools


Visualizing CUDS
----------------

The :func:`~simphony_mayavi.show.show` function is available to
visualise any top level CUDS container. The function will open a
window with a 3D view and a mayavi toolbar. The user can manipulate
the view and through the toolbar have access to common `mayavi
operations`_.

.. rubric:: Mesh example

.. literalinclude:: ../../examples/mesh_example.py

.. figure:: _images/mesh_show.png

.. rubric:: Lattice example

.. literalinclude:: ../../examples/lattice_example.py

.. figure:: _images/lattice_show.png

.. rubric:: Particles example

.. literalinclude:: ../../examples/particles_example.py

.. figure:: _images/particles_show.png

.. _mayavi operations: http://docs.enthought.com/mayavi/mayavi/mlab_changing_object_looks.html?highlight=toolbar#changing-object-properties-interactively
