SimPhoNy-Mayavi CHANGELOG
=========================

Release 0.4.4
-------------

- Backported fix converting data from VTK. Ref PR #198

Release 0.4.3/0.4.2
-------------------

- Adjustments against simphony-common v0.4

Release 0.4.1
-------------

- Fix test for adding EngineSource for different random seed (#182)
- Implemented SlimCUDSSource for improved memory consumption (#175)
- Fix keeping mlab.offscren option in snapshot (#178)
- Skip tests that require qt4 (#176)
- hypothesis is a development requirement, not a user's requirement (#179)


Release 0.4.0
-------------

- Support simphony-common 0.3.0 (#108)
- Added a SimPhoNy panel (GUI) for Mayavi2 (#110, #117)
- Added EngineManagerStandalone and EngineManagerStandaloneUI to the simphony plugin (#110)
- Implement EngineFactory class for creating registered simphony engine (#130)
- Support serialisation of CUDSSource, CUDSFileSource and EngineSource (#140)
- Support running a Python script for loading a SimPhoNy engine to the GUI (#143, #154)
- Added restore_scene in the simphony plugin for reproducing a visualisation easily (#145)
- Refactor default visualisation setup to default_module (#110, #120)
- Use numpy.float and numpy.int to handle dummy values (#115)

- Fix VTKParticles.from_dataset when dataset has no cell_types_array (#114)
- Fix cuba_data_accumulator so that it ignores CUBA.LATTICE_VECTORS (#137)
- Fix dev-requirement: Pillow instead of PIL should be used for testing images (#124)
- Fix dev-requirement: mock is required for testing (#113)

Release 0.3.1
-------------
- Corrections in setup.py regarding version number

Release 0.3.0
-------------
- Support simphony-common 0.2.1 and 0.2.2
- Support PrimitiveCell in VTKLattice
- Added lattice_tools for deducing primitive cells from data ported from tvtk.Dataset
- Check for invalid Bond before adding it to VTKParticles

Release 0.2.0
-------------

- Updated documentation and fixed mocking issues in automatic builds.
- Mayavi2 simphony plugin.
- Support loading tvk files into SimPhoNy CUDS containers.
- Support adapting  tvk.Datasets into SimPhoNy CUDS containers.
- Implement CUDSSource, a Mayavi source for SimPhoNy CUDS containers.
- Implement CUDSFileSource, a Mayavi source for SimPhoNy CUDS HDF5 Files.
- Implementation of VTKMesh, VTKParticles, VTKLattice objects wrapping vtk
  datasets and CUDS containers.
- CellCollection wrapper to wrap vtkCellArray into a MutableSequence.
- Fixed issue (#46).
- Fixed lattice point alignment in visualisation (#65).

Release 0.1.1
-------------

- Fix setup.py to install requirements.
- Add support for dual-build on travis-ci.

Release 0.1.0
-------------

This is the first official release of the Simphony-Mayavi plugin tools

- Support the first verison of the SimPhoNy-Mayavi visualization api
- Support simphony-common 0.1.0

- Setup Travis-Ci and Coveralls.io
- Documentation automatically build by readthedocs
- Added snapshot method
- Added show method
- Added LatticeSource to convert Lattice instances
- Added MeshShource to convert Mesh instances
- Added ParticlesShource to conver Particles instances
