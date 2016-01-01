from traits.api import HasTraits, Instance, ListStr, Str, List, Dict, Property
from traitsui.api import View, Group, VGroup, Item

from mayavi.core.trait_defs import DEnum

from simphony.cuds.abc_modeling_engine import ABCModelingEngine

from .basic_panel import BasicPanel


class EngineManager(BasicPanel):
    ''' A basic container of Simphony Engine that comes with a GUI.

    Additional panel can be added to support more operations related
    to the modeling engines

    Attributes
    ----------
    engines : dict
        Mappings of Simphony Modeling Engines in this manager

    Examples
    ---------
    >>> from simphony.engine import lammps   # LAMMPS

    >>> # Setup the engine so it is ready to run
    >>> dem = lammps.LammpsWrapper(...)   # experiment 1
    >>> dem2 = lammps.LammpsWrapper(...)  # experiment 2

    >>> # Setup for visualization
    >>> from simphony_mayavi.plugins.api import EngineManager
    >>> manager = EngineManager("exp1", dem)
    >>> manager.add_engine("exp2", dem2)

    >>> # ``engine_name`` is auto set as the last one being added
    >>> manager.engine_name
    "exp2"

    >>> # Add visualisation panel using mayavi
    >>> from simphony_mayavi.plugins.api import AddSourcePanel
    >>> from mayavi import mlab
    >>> manager.add_addon(AddSourcePanel(manager.engine_name,
                                         manager.engine,
                                         mlab.get_engine()))

    >>> # AddSourcePanel comes with a public method ``add_dataset_to_scene``
    >>> # Visualise the Engine's CUDS dataset "particles" in Mayavi
    >>> manager.add_dataset_to_scene("particles")  # from ``dem2``

    >>> # when a different engine is selected, the added panel can see
    >>> # it too
    >>> manager.engine_name = "exp1"
    >>> manager.add_dataset_to_scene("particles")  # from ``dem``

    >>> # GUI for interactive control
    >>> manager.show_config()
    '''
    # Engines that are added to the manager
    engines = Dict(Str, Instance(ABCModelingEngine))

    # Names of engines in the Manager
    _engine_names = ListStr

    # Selected engine (overloaded BasicPanel)
    engine = Property(depends_on="engine_name")

    # Selected engine name
    engine_name = DEnum(values_name="_engine_names")

    # Traits view
    trait_view = View(Group(Item("engine_name", label="Engine Wrapper")),
                      resizable=True)
    # ----------------------------------------------------
    # Traits Property
    # ----------------------------------------------------

    def _get_engine(self):
        return self.engines[self.engine_name]

    def add_engine(self, name, modeling_engine):
        if name in self.engines:
            raise ValueError("{} is already added".format(name))
        self.engines[name] = modeling_engine
        self._engine_names = self.engines.keys()
        self.engine_name = name

    def remove_engine(self, name):
        ''' Remove a modeling engine from the manager'''
        if name not in self.engines:
            msg = "{} is not an engine in this manager"
            raise KeyError(msg.format(name))

        if len(self.engines) == 1:
            msg = ("There will be no more engine if {} is removed. "
                   "Not removing it.")
            raise IndexError(msg.format(name))

        self.engines.pop(name)
        self._engine_names = self.engines.keys()

    # --------------------------------------------------------
    # Integrate panels' UI
    # --------------------------------------------------------

    def show_config(self):
        ''' Show the GUI for interactive control '''
        panel_mapping = {"object{}".format(index): panel
                         for index, panel in enumerate(self.panels)}
        panel_mapping["object"] = self

        panel_views = []
        for index, panel in enumerate(self.panels):
            view = panel.trait_view().content.content[0]
            panel_views.append(view)

        all_panels = VGroup(Item("engine_name", label="Engine Wrapper"),
                            Group(*panel_views, layout="tabbed"))
        for index, inner_group in enumerate(all_panels.content[1].content):
            inner_group.object = "object{}".format(index)

        self.edit_traits(view=View(all_panels), context=panel_mapping)
