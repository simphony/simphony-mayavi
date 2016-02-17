from itertools import izip
import logging

from apptools.persistence.state_pickler import (load_state, set_state,
                                                update_state, StateSetterError)
from mayavi.core.common import handle_children_state
from mayavi import mlab

logger = logging.getLogger(__name__)


def restore_scene(saved_visualisation, scene_index=0):
    ''' Restore the current scene and children of data sources
    according to the visualisation previously saved.

    Unmatched data sources are ignored.  Say the current
    scene has only two data sources while the saved scene has
    three, setting for the third data source is ignored.

    Parameters
    ----------
    saved_visualisation : file or fileobj

    scene_index : int
        index of the scene in the saved visualisation.
        default: 0 (first scene)
    '''
    # get the state of the visualisation
    state = load_state(saved_visualisation)
    update_state(state)

    # reference scene
    ref_scene = state.scenes[scene_index]

    # data sources in the reference scene
    ref_sources = ref_scene.children

    # the scene to be restored
    current_scene = mlab.gcf()

    # data sources in the current scene
    current_sources = current_scene.children

    # warn the user about mismatch data sources
    if len(current_sources) != len(ref_sources):
        msg = ("Current scene has {} sources while the reference has {}. "
               "Mismatch sources are ignored")
        logger.warning(msg.format(len(current_sources), len(ref_sources)))

    # Restore the children for each data source
    # unmatched sources are ignored
    for current_source, ref_source in izip(current_sources, ref_sources):

        # Setup the children
        handle_children_state(current_source.children, ref_source.children)

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
