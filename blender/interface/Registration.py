import importlib

import bpy
from bpy.props import PointerProperty
from bpy.utils import register_class

from blender.interface import Properties, Panels, Operators, install_dependencies, Preferences


importlib.reload(Operators)
importlib.reload(Panels)
importlib.reload(Properties)
importlib.reload(Preferences)
importlib.reload(install_dependencies)


def get_classes():
    from management import detection_operator
    importlib.reload(detection_operator)

    classes = (
        Properties.MyProperties,

        Operators.UI_detection_button,
        Operators.UI_transfer_anim_button,
        detection_operator.DetectionModalOperator,

        Panels.UI_PT_main_panel,
    )
    return classes


def get_preferences():
    preference_classes = (Preferences.PREFERENCES_OT_install_dependencies_button,
                          Preferences.EXAMPLE_preferences,
                          Panels.UI_PT_warning_panel)
    return preference_classes


def register():
    for m_class in get_preferences():
        register_class(m_class)

    try:
        for dependency in install_dependencies.dependencies:
            install_dependencies.import_module(module_name=dependency.module, global_name=dependency.name)
        install_dependencies.dependencies_installed = True
    except ModuleNotFoundError:
        # Don't register other panels, operators etc.
        return

    register_user_interface()


def register_user_interface():
    for cls in get_classes():
        print(str(cls))
        register_class(cls)
    bpy.types.Scene.m_cgtinker_mediapipe = PointerProperty(type=Properties.MyProperties)


def manual_test_registration():
    for cls in get_classes():
        print(str(cls))
        register_class(cls)
    bpy.types.Scene.m_cgtinker_mediapipe = PointerProperty(type=Properties.MyProperties)


def unregister():
    from bpy.utils import unregister_class

    for cls in get_preferences():
        unregister_class(cls)
        print(str(cls))

    if install_dependencies.dependencies_installed:
        classes = get_classes()
        for cls in reversed(classes):
            print(str(cls))
            unregister_class(cls)
        del bpy.types.Scene.m_cgtinker_mediapipe
