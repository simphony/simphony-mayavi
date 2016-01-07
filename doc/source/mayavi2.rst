Mayavi2
=======

The Simphony-Mayavi library provides a plugin for Mayavi2 to easily
create mayavi ``Source`` instances from SimPhoNy CUDS containers and
files. With the provided tools one can use the SimPhoNy libraries to
work inside the Mayavi2 application, as it is demonstrated in the
examples.
 
Open CUDS Files in Mayavi2
--------------------------

In order for mayavi2 to understand ``*.cuds`` files one needs to make
sure that the simpony_mayavi plugin has been selected and activated in
the Mayavi2 preferences dialog.

.. figure:: _images/mayavi2_preferences_setup.png
   :figwidth: 80%

   Cuds files are supported in the ``Open File..`` dialog. After running
   the :download:`provided example <../../examples/cuds_file_mayavi2.py>`,
   load the ``example.cuds`` file into Mayavi2.

.. figure:: _images/mayavi2_load_cuds_dialog.png
   :figwidth: 80%

.. figure:: _images/mayavi2_load_cuds_example.png
   :figwidth: 80%

   When loaded a CUDSFile is converted into a Mayavi Source and the
   user can add normal Mayavi modules to visualise the currently
   selected CUDS container from the available containers in the file.

   In the example we load the container named ``cubic`` and attach the
   Glyph module to draw a cone at each point to visualise ``TEMPERATURE``
   and ``VELOCITY`` in the Mayavi Scene.


View CUDS in Mayavi2
--------------------

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


Interact with Simphony Engine within Mayavi2
--------------------------------------------

A Mayavi2 plugin similar to the
:class:`~simphony_mayavi.plugins.engine_manager_standalone_ui.EngineManagerStandaloneUI`
described in :ref:`engine-manager-standalone-label` is provided. In order to use it,
one needs to first activate the plugin in ``Preferences``, following the instructions
in `Open CUDS Files in Mayavi2`_. **Restart** Mayavi2. Then the EngineManager panel
can be added by selecting
``View`` --> ``Other...`` --> ``Simphony Engine to Mayavi2``.

.. figure:: _images/engine_manager_mayavi2_setup.png

   Add the Simphony Engine Manager panel

The Engine Manager is binded to the Python shell within Mayavi2 as
``simphony_panel``.  Simphony modeling engines can be added or
removed from the panel using :func:`~simphony_mayavi.plugins.engine_manager.add_engine`
and :func:`~simphony_mayavi.plugins.engine_manager.remove_engine`.

.. rubric:: Inside the Mayavi2 Python shell

.. code-block:: python

   from simphony_mayavi.sources.tests import testing_utils
   engine = testing_utils.DummyEngine()
   simphony_panel.add_engine("Test", engine)

.. figure:: _images/engine_manager_mayavi2.png
	   
