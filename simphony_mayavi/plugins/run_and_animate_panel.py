from pyface.api import MessageDialog
from traits.api import Float, Int, Bool, HasTraits, Instance, Event
from traitsui.api import View, VGroup, HGroup, Item, ButtonEditor

from simphony.core.cuba import CUBA
from simphony.cuds.abc_modeling_engine import ABCModelingEngine

from .run_and_animate import RunAndAnimate


class RunAndAnimatePanel(HasTraits):
    ''' GUI for running a Simphony Modeling Engine and animating
    the result in an existing scene

    Attributes
    ----------
    engine : Instance of ABCModelingEngine
        Simphony Engine
    mayavi_engine : mayavi.core.engine.Engine instance
        for retrieving current scenes
    time_step : float
        CUBA.TIME_STEP of the Simphony Engine
    number_of_time_steps : float
        CUBA.NUMBER_OF_TIME_STEPS of the Simphony Engine
    '''

    engine = Instance(ABCModelingEngine)

    mayavi_engine = Instance("mayavi.core.engine.Engine")

    handler = Instance(RunAndAnimate)

    # Label to be displayed in tab
    label = "Run/Animate"

    # -------------------------------------------------------
    # Basic time step parameters to interact with the engine
    # -------------------------------------------------------
    time_step = Float(allow_none=False)
    number_of_time_steps = Float(allow_none=False)

    # ----------------------------------------------
    # For running the engine and animating scenes
    # (Only relevant to UI)
    # ----------------------------------------------
    _number_of_runs = Int(1)
    _animate = Event
    _update_all_scenes = Bool(False)

    panel_view = View(
        VGroup(
            Item("time_step"),
            Item("number_of_time_steps"),
            HGroup(Item(name="_number_of_runs", label="Runs for"),
                   Item(label="time(s)")),
            HGroup(Item("_animate", show_label=False,
                        enabled_when="engine",
                        editor=ButtonEditor(label="Animate")),
                   Item(name="_update_all_scenes", label="Update all scenes")),
            ),
        title="Run and Animate")

    # ------------------------------------------------------------
    # UI operation
    # ------------------------------------------------------------

    def __animate_fired(self):
        try:
            self.handler.animate(self._number_of_runs, ui=True,
                                 update_all_scenes=self._update_all_scenes)
        except RuntimeError as exception:
            message_dialog = MessageDialog()
            message_dialog.error(exception.message)

    # ----------------------------------------------------------
    # Trait handlers
    # ----------------------------------------------------------

    def _handler_default(self):
        return RunAndAnimate(self.engine, self.mayavi_engine)

    def _engine_changed(self):
        self.handler.engine = self.engine

        # Close existing animator UI
        if (self.handler._animator and self.handler._animator.ui and
                not self.handler._animator.ui.destroyed):
            self.handler._animator.close()

        # Update run parameters in the UI
        self._setup_run_parameters()

    def _mayavi_engine_changed(self):
        self.handler.mayavi_engine = self.mayavi_engine

    def _time_step_changed(self):
        self.engine.CM[CUBA.TIME_STEP] = self.time_step

    def _number_of_time_steps_changed(self):
        value = self.number_of_time_steps
        self.engine.CM[CUBA.NUMBER_OF_TIME_STEPS] = value

    # ----------------------------------------------------------
    # Public methods
    # ----------------------------------------------------------

    def show_config(self):
        ''' Show the GUI '''
        return self.edit_traits(view="panel_view", kind="live")

    # ------------------------------------------------------------
    # Private methods
    # ------------------------------------------------------------

    def _setup_run_parameters(self):
        CM = self.engine.CM

        # For interacting with the engine
        if CUBA.TIME_STEP in CM:
            self.time_step = CM[CUBA.TIME_STEP]
        else:
            text = "engine.CM[TIME_STEP] is not found."
            message_dialog = MessageDialog()
            message_dialog.error(text)

        if CUBA.NUMBER_OF_TIME_STEPS in CM:
            value = CM[CUBA.NUMBER_OF_TIME_STEPS]
            self.number_of_time_steps = value
        else:
            text = "engine.CM[NUMBER_OF_TIME_STEPS] is not found."
            message_dialog = MessageDialog()
            message_dialog.error(text)
