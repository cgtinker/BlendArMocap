import bpy
from bpy.props import PointerProperty
from bpy.utils import register_class, unregister_class

from . import ui_properties, ui_panels, pref_operators, pref_panels, ui_operators
from ..utils import dependencies


def get_classes():
    # getting classes to avoid loading possibly unavailable packages
    classes = (
        ui_properties.CgtProperties,

        ui_operators.UI_transfer_anim_button,
        ui_operators.UI_toggle_drivers_button,
        ui_operators.WM_modal_detection_operator,

        ui_panels.UI_PT_main_panel,
        # ui_panels.UI_PT_RemappingPanel
    )
    return classes


def get_preferences():
    preference_classes = (pref_operators.PREFERENCES_OT_install_dependencies_button,
                          pref_operators.PREFERENCES_OT_uninstall_dependencies_button,
                          pref_panels.BLENDARMOCAP_preferences,
                          ui_panels.UI_PT_warning_panel)
    return preference_classes


def register():
    print('Registing BlendArMocap\n')

    for m_class in get_preferences():
        # print(m_class)
        register_class(m_class)

    try:
        print('Try to access dependencies')
        for dependency in dependencies.required_dependencies:
            pkg_info = dependencies.get_package_info(dependency)
            print(dependency.module, pkg_info)

        if dependencies.dependencies_installed:
            register_user_interface()

    except ModuleNotFoundError:
        # Don't register other panels, ui_operators etc.
        print('REGISTRATION FAILED: REQUIRED MODULE NOT FOUND')
        return


def register_user_interface():
    for cls in get_classes():
        try:
            register_class(cls)
        except ValueError:
            print("Class has already been registered:", cls)

    bpy.types.Scene.m_cgtinker_mediapipe = PointerProperty(type=ui_properties.CgtProperties)


def unregister():
    print("Unregister BlendArMocap")
    for cls in get_preferences():
        try:
            unregister_class(cls)
        except RuntimeError:
            # Class may not be registered
            pass

    if dependencies.dependencies_installed:
        unregister_ui_panels()


def unregister_ui_panels():
    classes = get_classes()
    for cls in reversed(classes):
        try:
            unregister_class(cls)
        except RuntimeError:
            print("Class may not be registered:", cls)

    del bpy.types.Scene.m_cgtinker_mediapipe  # noqa


def manual_unregistration():
    print("MANUAL UNREGISTER")
    classes = get_classes()
    for cls in reversed(classes):
        unregister_class(cls)

    del bpy.types.Scene.m_cgtinker_mediapipe # noqa


def manual_test_registration():
    print("MANUAL REGISTER")
    for cls in get_classes():
        register_class(cls)

    bpy.types.Scene.m_cgtinker_mediapipe = PointerProperty(type=ui_properties.CgtProperties)
