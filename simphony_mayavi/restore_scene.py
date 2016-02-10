from future_builtins import zip
import logging

from apptools.persistence.state_pickler import (load_state, set_state,
                                                update_state, StateSetterError)
from mayavi.core.common import handle_children_state
from mayavi import mlab

logger = logging.getLogger(__name__)


def restore_scene(saved_visualisation):
    ''' Restore the current scene and children of data sources
    according to the visualisation previously saved.

    If the saved visualisation has multiple scenes, the first
    non-empty scene is used and the rest are ignored.

    Unmatched data sources are also ignored.  Say the current
    scene has only two data sources while the saved scene has
    three, setting for the third data source is ignored.

    Parameters
    ----------
    saved_visualisation : file or fileobj
    '''

    current_scene = mlab.gcf()

    # get the state of the visualisation
    state = load_state(saved_visualisation)
    update_state(state)

    # find the first scene that is not empty
    for ref_scene in state.scenes:
        if len(ref_scene.children) > 0:
            break
    else:
        msg = "There is no non-empty scene in the saved visualisation"
        raise ValueError(msg)

    # restore the children for each source
    current_sources = current_scene.children
    ref_sources = ref_scene.children

    # warn the user about mismatch data sources
    if len(current_sources) != len(ref_sources):
        msg = ("Current scene has {} sources while the reference has {}. "
               "Mismatch sources are ignored")
        logger.warning(msg.format(len(current_sources), len(ref_sources)))

    # Restore the children for each data source
    # unmatched sources are ignored
    for current_source, ref_source in zip(current_sources, ref_sources):

        # Setup the children
        handle_children_state(current_source.children, ref_source.children)

        try:
            set_state(current_source, ref_source, first=["children"],
                      ignore=["*"])
        except StateSetterError:
            # if current_source and ref_source do not have the same class
            # state_pickler.set_state cannot be applied
            # Try restoring each child separately
            # if __set_pure_state__ method is available,
            # we are by-passing the state_pickler.set_state
            for current_child, ref_child in zip(current_source.children,
                                                ref_source.children):
                if hasattr(current_child, "__set_pure_state__"):
                    current_child.__set_pure_state__(ref_child)
                else:
                    set_state(current_child, ref_child)

    # work around for the bug in restoring camera
    # https://github.com/enthought/mayavi/issues/283
    ref_scene.scene.camera.pop("distance", None)

    # restore scene setting
    try:
        set_state(current_scene.scene, ref_scene.scene)
    except StateSetterError:
        # current scene is an instance of a different class
        # at least restore the camera
        set_state(current_scene.scene.camera,
                  ref_scene.scene.camera)
