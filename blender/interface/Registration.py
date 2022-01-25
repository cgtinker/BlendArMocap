import importlib

import bpy
from bpy.props import PointerProperty
from bpy.utils import register_class

from blender.interface import Properties, Panels, Operators, install_dependencies, Preferences
from management import detection_operator

importlib.reload(Operators)
importlib.reload(Panels)
importlib.reload(Properties)
importlib.reload(detection_operator)
importlib.reload(Preferences)
importlib.reload(install_dependencies)

classes = (
    Properties.MyProperties,

    Operators.UI_detection_button,
    Operators.UI_transfer_anim_button,
    detection_operator.DetectionModalOperator,

    Panels.UI_PT_main_panel,
)

preference_classes = (Preferences.PREFERENCES_OT_install_dependencies_button,
                      Preferences.EXAMPLE_preferences,
                      Panels.UI_PT_warning_panel)


def register():
    for m_class in preference_classes:
        register_class(m_class)

    try:
        for dependency in install_dependencies.dependencies:
            install_dependencies.import_module(module_name=dependency.module, global_name=dependency.name)
        dependencies_installed = True
    except ModuleNotFoundError:
        # Don't register other panels, operators etc.
        return

    for cls in classes:
        register_class(cls)
    bpy.types.Scene.m_cgtinker_mediapipe = PointerProperty(type=Properties.MyProperties)


def manual_test_registration():
    for m_class in classes:
        register_class(m_class)
    bpy.types.Scene.m_cgtinker_mediapipe = PointerProperty(type=Properties.MyProperties)


def unregister():
    from bpy.utils import unregister_class

    for cls in preference_classes:
        unregister_class(cls)

    if install_dependencies.dependencies_installed:
        for cls in reversed(classes):
            unregister_class(cls)
        del bpy.types.Scene.m_cgtinker_mediapipe
