import logging
import bpy
from ..cgt_core.cgt_utils import cgt_user_prefs
from . import cgt_mp_interface, cgt_mp_preferences, cgt_mp_detection_operator, cgt_mp_properties


classes = [
    cgt_mp_properties,
    cgt_mp_detection_operator,
    cgt_mp_interface,
    cgt_mp_preferences
]

MP_ATTRS = {
    "local_user": False,
    "key_frame_step": 4,
    "webcam_input_device": 0,
    "detection_input_type": "movie",
    "enum_detection_type": "HAND",
    "enum_stream_dim": "sd",
    "enum_stream_type": "0",
    "min_detection_confidence": 0.5,
    "hand_model_complexity": 1,
    "pose_model_complexity": 1,
    "holistic_model_complexity": 1,
    "refine_face_landmarks": False
}


@bpy.app.handlers.persistent
def save_preferences(*args):
    user = bpy.context.scene.cgtinker_mediapipe  # noqa
    cgt_user_prefs.set_prefs(**{attr: getattr(user, attr, default) for attr, default in MP_ATTRS.items()})


@bpy.app.handlers.persistent
def load_preferences(*args):
    stored_preferences = cgt_user_prefs.get_prefs(**MP_ATTRS)
    user = bpy.context.scene.cgtinker_mediapipe # noqa
    for property_name, value in stored_preferences.items():
        if not hasattr(user, property_name):
            logging.warning(f"{property_name} - not available.")
        setattr(user, property_name, value)


def register():
    for cls in classes:
        if cls is None:
            continue
        cls.register()

    bpy.app.handlers.save_pre.append(save_preferences)
    bpy.app.handlers.load_post.append(load_preferences)


def unregister():
    for cls in reversed(classes):
        if cls is None:
            continue
        cls.unregister()

