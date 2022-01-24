import importlib

import bpy
from bpy.props import PointerProperty
from bpy.utils import register_class

from blender.interface import Preferences
from blender.interface import Properties, Panels, Operators
from management import detection_operator

importlib.reload(Operators)
importlib.reload(Panels)
importlib.reload(Properties)
importlib.reload(detection_operator)
importlib.reload(Preferences)

classes = (
    Properties.MyProperties,

    Operators.UI_detection_button,
    Operators.UI_transfer_anim_button,
    detection_operator.DetectionModalOperator,

    Panels.UI_PT_main_panel,
)

preference_classes = (Panels.UI_PT_warning_panel,
                      Preferences.EXAMPLE_OT_install_dependencies,
                      Preferences.EXAMPLE_preferences)


def register():
    for m_class in preference_classes:
        register_class(m_class)


def manual_test_registration():
    for m_class in classes:
        register_class(m_class)
    bpy.types.Scene.m_cgtinker_mediapipe = PointerProperty(type=Properties.MyProperties)


def unregister():
    from bpy.utils import unregister_class
    for m_class in reversed(classes):
        unregister_class(m_class)
    del bpy.types.Scene.m_cgtinker_mediapipe
