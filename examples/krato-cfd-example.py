""" Modified from simphony-kratos/simkratos/tests/cfd/test_kratos_cfd.py
"""
import os

from simphony.core.cuba import CUBA
from simphony.engine import kratos

from KratosMultiphysics import *
from KratosMultiphysics.IncompressibleFluidApplication import *
from KratosMultiphysics.FluidDynamicsApplication import *
from KratosMultiphysics.ExternalSolversApplication import *
from KratosMultiphysics.MeshingApplication import *


path = str(os.path.join(
    os.path.dirname(__file__),
    "CFD_exampleFluid"
))

time_step = 0.001
num_steps = 5


utils = kratos.CFD_Utils()
wrapper = kratos.CFDWrapper()

wrapper.CM[CUBA.TIME_STEP] = time_step
wrapper.CM[CUBA.NUMBER_OF_TIME_STEPS] = num_steps

# Set the meshes that are part of the fluid
wrapper.SPE[kratos.CUBAExt.FLUID_MESHES] = [
    "fluid_0", "fluid_1", "fluid_2",
    "fluid_3", "fluid_4"
]

# reads kratos data so its interpretable by simphony
kratos_model = utils.read_modelpart(path)

wrapper.BC[CUBA.VELOCITY] = {}
wrapper.BC[CUBA.PRESSURE] = {}

for mesh in kratos_model['meshes']:
    wrapper.add_dataset(mesh)

for bc in kratos_model['bcs']:
    wrapper.BC[CUBA.VELOCITY][bc['name']] = bc['velocity']
    wrapper.BC[CUBA.PRESSURE][bc['name']] = bc['pressure']

from simphony.visualisation import mayavi_tools
mayavi_tools.add_engine_to_mayavi2("kratos", wrapper)
