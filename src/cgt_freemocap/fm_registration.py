import bpy
import logging
from . import fm_interface
from . import fm_operators
from ..cgt_core.cgt_utils import cgt_user_prefs


modules = [
    fm_operators,
    fm_interface
]


FM_ATTRS = {
    "load_raw": False,
    "quickload": False,
}


@bpy.app.handlers.persistent
def save_preferences(*args):
    user = bpy.context.scene.cgtinker_freemocap  # noqa
    cgt_user_prefs.set_prefs(**{attr: getattr(user, attr, default) for attr, default in FM_ATTRS.items()})


@bpy.app.handlers.persistent
def load_preferences(*args):
    stored_preferences = cgt_user_prefs.get_prefs(**FM_ATTRS)
    user = bpy.context.scene.cgtinker_freemocap # noqa
    for property_name, value in stored_preferences.items():
        if not hasattr(user, property_name):
            logging.warning(f"{property_name} - not available.")
        setattr(user, property_name, value)


def register():
    for module in modules:
        module.register()

    bpy.app.handlers.save_pre.append(save_preferences)
    bpy.app.handlers.load_post.append(load_preferences)


def unregister():
    for module in reversed(modules):
        module.unregister()

