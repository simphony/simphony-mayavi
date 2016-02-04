from traits.api import Enum
from traitsui.api import View, Item

from .abc_engine_factory import ABCEngineFactory


class KratosEngineFactory(ABCEngineFactory):

    model = Enum("CFD", "DEM")

    view = View(Item("model"), buttons=["OK", "Cancel"])

    def create(self):
        from simphony.engine import kratos

        if self.model == "CFD":
            return kratos.CFDWrapper()
        elif self.model == "DEM":
            return kratos.DEMWrapper()


ENGINE_REGISTRY = dict(kratos=KratosEngineFactory())
