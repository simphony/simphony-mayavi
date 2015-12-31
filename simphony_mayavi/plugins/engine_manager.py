from traits.api import HasTraits, Instance, ListStr, Str, List, Dict, Property
from traitsui.api import View, Group, VGroup, Item

from mayavi.core.trait_defs import DEnum

from simphony.cuds.abc_modeling_engine import ABCModelingEngine

from .basic_panel import BasicPanel


class EngineManager(HasTraits):
    ''' A basic container of Simphony Engine that comes with a GUI.

    Additional panel can be added to support more operations related
    to the modeling engines

    Attributes
    ----------
    engines : dict
        { name_of_engine: ModelingEngine }
    current_engine : ModelingEngine
        Simphony Modeling Engine Wrapper
    engine_name : str
        Name for the engine currently selected (unique for each engine)
    engine_names : list
        All of the engine names
    panels : list
        List of addons

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
                                         manager.current_engine,
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
    engine_names = ListStr

    # Selected engine
    current_engine = Property(depends_on="engine_name")

    # Selected engine name
    engine_name = DEnum(values_name="engine_names")

    # Traits view
    traits_view = View(Group(Item("engine_name", label="Engine Wrapper")),
                       resizable=True)

    # addon panels
    panels = List(Instance(BasicPanel))

    # ----------------------------------------------------
    # Traits Property
    # ----------------------------------------------------

    def _get_current_engine(self):
        return self.engines[self.engine_name]

    # ----------------------------------------------------
    # Traits Handler
    # ----------------------------------------------------

    def _engine_name_changed(self):
        for panel in self.panels:
            panel.engine = self.current_engine
            panel.engine_name = self.engine_name

    # ----------------------------------------------------
    # Initialization
    # ----------------------------------------------------

    def __init__(self, engine_name, modeling_engine):
        '''
        Parameters
        ----------
        engine_name : str
            Name of the engine
        modeling_engine : Instance of ABCModelingEngine
            Simphony Modeling Engine Wrapper
        '''
        self.add_engine(engine_name, modeling_engine)

    # -----------------------------------------------------------
    # Public methods
    # -----------------------------------------------------------

    def add_addon(self, panel):
        ''' Add a panel to the EngineManager

        Public methods from the panel would be added to the EngineManager.
        Methods of the same name would be overloaded.  The default trait_view
        of the panel would be added as a tab in the EngineManager.

        Parameter
        ---------
        panel : Instance of BasicPanel
            Example: AddSourcePanel, RunAndAnimatePanel
        '''
        panel.engine = self.current_engine
        panel.engine_name = self.engine_name
        self.panels.append(panel)

        # add public method
        # methods with the same name would be overloaded
        for public_method in panel.public_methods:
            setattr(self, public_method.__name__, public_method)

    def add_engine(self, name, modeling_engine):
        if name in self.engines:
            raise ValueError("{} is already added".format(name))
        self.engines[name] = modeling_engine
        self.engine_names = self.engines.keys()
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
        self.engine_names = self.engines.keys()

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
