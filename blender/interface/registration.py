import importlib

import bpy
from bpy.props import PointerProperty
from bpy.utils import register_class

from blender.interface import properties, ui_panels, ui_operators, install_dependencies, ui_preferences


importlib.reload(ui_operators)
importlib.reload(ui_panels)
importlib.reload(properties)
importlib.reload(ui_preferences)
importlib.reload(install_dependencies)


def get_classes():
    from management import detection_operator
    importlib.reload(detection_operator)

    classes = (
        properties.MyProperties,

        ui_operators.UI_detection_button,
        ui_operators.UI_transfer_anim_button,
        detection_operator.DetectionModalOperator,

        ui_panels.UI_PT_main_panel,
    )
    return classes


def get_preferences():
    preference_classes = (ui_preferences.PREFERENCES_OT_install_dependencies_button,
                          ui_preferences.EXAMPLE_preferences,
                          ui_panels.UI_PT_warning_panel)
    return preference_classes


def register():
    for m_class in get_preferences():
        register_class(m_class)

    try:
        for dependency in install_dependencies.dependencies:
            install_dependencies.import_module(module_name=dependency.module, global_name=dependency.name)
        install_dependencies.dependencies_installed = True
    except ModuleNotFoundError:
        # Don't register other panels, ui_operators etc.
        return

    register_user_interface()


def register_user_interface():
    for cls in get_classes():
        print(str(cls))
        register_class(cls)
    bpy.types.Scene.m_cgtinker_mediapipe = PointerProperty(type=properties.MyProperties)


def manual_test_registration():
    for cls in get_classes():
        print(str(cls))
        register_class(cls)
    bpy.types.Scene.m_cgtinker_mediapipe = PointerProperty(type=properties.MyProperties)


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
