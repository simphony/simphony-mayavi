Mayavi2
=======

The Simphony-Mayavi library provides a plugin for Mayavi2 easily create
mayavi ``Source`` instances from SimPhoNy CUDS containers and
files. With the provided tools one can use the SimPhoNy libraries to
work inside the Mayavi2 application, as it is demonstrated in the
examples.

.. rubric:: Setup plugin

To setup the mayavi2 plugin one needs to make sure that the
simpony_mayavi plugin has been selected and activated in the Mayavi2
preferences dialog.

.. figure:: _images/mayavi2_preferences_setup.png
   :figwidth: 80%

.. rubric:: Source from a CUDS Mesh

.. literalinclude:: ../../examples/mesh_mayavi2.py

.. figure:: _images/mayavi2_mesh.png
   :figwidth: 80%

   Use the provided example to create a CUDS Mesh and visualise
   directly in Mayavi2.

.. rubric:: Source from a CUDS Lattice

.. literalinclude:: ../../examples/lattice_mayavi2.py

.. figure:: _images/mayavi2_lattice.png
   :figwidth: 80%

   Use the provided example to create a CUDS Lattice and visualise
   directly in Mayavi2.

.. rubric:: Source for a CUDS Particles

.. literalinclude:: ../../examples/particles_mayavi2.py

.. figure:: _images/mayavi2_particles.png
   :figwidth: 80%

   Use the provided example to create a CUDS Particles and visualise
   directly in Mayavi2.

.. rubric:: Source from a CUDS File

.. literalinclude:: ../../examples/cuds_file_mayavi2.py

.. figure:: _images/mayavi2_cuds_file.png
   :figwidth: 80%

   Cuds files are supported in the ``Open File..`` dialog.

.. figure:: _images/mayavi2_load_cuds_example.png
   :figwidth: 80%

   When loaded a CUDSFile is converted into a Mayavi Source and the
   user can add normal Mayavi modules to visualise the currently
   selected CUDS container from the available containers in the file.

   In the example we load the container named ``cubic`` and attach the
   Glyph module to draw a cone at each point to visualise ``TEMPERATURE``
   and ``VELOCITY`` in the Mayavi Scene.
