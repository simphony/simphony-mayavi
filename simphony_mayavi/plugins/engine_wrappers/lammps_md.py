from traits.api import Enum
from traitsui.api import View, Item

from .abc_engine_factory import ABCEngineFactory


class LammpsEngineFactory(ABCEngineFactory):

    interface = Enum("File-IO", "Internal")

    view = View(Item("interface"), buttons=["OK", "Cancel"])

    def create(self):
        from simphony.engine import lammps

        if self.interface == "File-IO":
            return lammps.LammpsWrapper(use_internal_interface=False)
        elif self.interface == "Internal":
            return lammps.LammpsWrapper(use_internal_interface=True)


ENGINE_REGISTRY = dict(lammps=LammpsEngineFactory())
