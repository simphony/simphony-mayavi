""" Modified from simphony-lammps-md/examples/dem_billiards/dem_billiards.py
Requires file:
github.com/simphony/simphony-lammps-md/examples/dem_billiards/billiards_init.data
"""
import os

from simphony.engine import lammps

from simlammps import EngineType
from simphony.core.cuba import CUBA

# read data
particles = lammps.read_data_file(
    os.path.join(os.path.dirname(__file__),
                 "billiards_init.data"))[0]

# configure dem-wrapper
dem = lammps.LammpsWrapper(engine_type=EngineType.DEM)

dem.CM_extension[lammps.CUBAExtension.THERMODYNAMIC_ENSEMBLE] = "NVE"
dem.CM[CUBA.NUMBER_OF_TIME_STEPS] = 1000
dem.CM[CUBA.TIME_STEP] = 0.001

# Define the BC component of the SimPhoNy application model:
dem.BC_extension[lammps.CUBAExtension.BOX_FACES] = ["fixed",
                                                    "fixed",
                                                    "fixed"]
dem.BC_extension[lammps.CUBAExtension.BOX_VECTORS] = None

# add particles to engine
dem.add_dataset(particles)

# Run the engine
dem.run()
