from traits.api import HasTraits, Instance, ListStr, Str, Dict, Property
from traitsui.api import View, Group, Item

from mayavi.core.trait_defs import DEnum

from simphony.cuds.abc_modeling_engine import ABCModelingEngine


class EngineManager(HasTraits):
    ''' A basic container of Simphony Engine that comes with a GUI.

    Additional panel can be added to support more operations related
    to the modeling engines

    Attributes
    ----------
    engines : dict
        Mappings of Simphony Modeling Engines in this manager
    engine_name : str
        Name of the Simphony Modeling Engine
    engine : Instance of ABCModelingEngine
        Simphony Modeling Engine
    '''
    # Engines that are added to the manager
    engines = Dict(Str, Instance(ABCModelingEngine))

    # Names of engines in the Manager
    _engine_names = ListStr

    # Selected engine
    engine = Property(depends_on="engine_name")

    # Selected engine name
    engine_name = DEnum(values_name="_engine_names")

    # Traits view
    traits_view = View(Group(Item("engine_name", label="Engine Wrapper")),
                       resizable=True)
    # ----------------------------------------------------
    # Traits Property
    # ----------------------------------------------------

    def _get_engine(self):
        if self.engine_name in self.engines:
            return self.engines[self.engine_name]
        else:
            return None

    def _set_engine(self, value):
        if value not in self.engines.values():
            msg = "{} is not an engine in the manager.  Use ``add_engine()``"
            raise ValueError(msg.format(value))
        for name, engine in self.engines.items():
            if value is engine:
                self.engine_name = name
                break

    # ------------------------------------------------------
    # Public methods
    # ------------------------------------------------------

    def add_engine(self, name, modeling_engine):
        ''' Add a Simphony Engine to the manager

        Parameters
        ----------
        name : str
            Name to be associated with the modeling engine
        modeling_engine : Instance of ABCModelingEngine
            Simphony Engine Wrapper
        '''
        if name in self.engines:
            raise ValueError("{} is already added".format(name))
        self.engines[name] = modeling_engine
        self._engine_names = self.engines.keys()

    def remove_engine(self, name):
        ''' Remove a modeling engine from the manager.
        If modeling engine to be removed is currently selected,
        select the one of the remaining engines

        Parameter
        ---------
        name : str
            Name associated with the engine to be removed
        '''
        if name not in self.engines:
            msg = "{} is not an engine in this manager"
            raise KeyError(msg.format(name))

        if len(self.engines) == 1:
            msg = ("There will be no more engine if {} is removed. "
                   "Not removing it.")
            raise IndexError(msg.format(name))

        self.engines.pop(name)
        if self.engine_name == name:
            self.engine_name = self.engines.keys()[0]
        self._engine_names = self.engines.keys()
