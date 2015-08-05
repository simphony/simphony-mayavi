SimPhoNy-Mayavi CHANGELOG
=========================

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
