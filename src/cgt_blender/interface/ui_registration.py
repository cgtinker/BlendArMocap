import bpy
from bpy.props import PointerProperty
from bpy.utils import register_class, unregister_class

from . import ui_properties, ui_panels, pref_operators, pref_panels, ui_operators
from ..utils import install_dependencies


def get_classes():
    # getting classes to avoid loading possibly unavailable packages
    classes = (
        ui_properties.CgtProperties,

        ui_operators.UI_transfer_anim_button,
        ui_operators.UI_toggle_drivers_button,
        ui_operators.WM_modal_detection_operator,

        ui_panels.UI_PT_main_panel,
        ui_panels.UI_PT_RemappingPanel
    )
    return classes


def get_preferences():
    preference_classes = (pref_operators.PREFERENCES_OT_install_dependencies_button,
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
        for dependency in install_dependencies.dependencies:
            print(str(dependency))
            install_dependencies.import_module(module_name=dependency.module, global_name=dependency.name)
        install_dependencies.dependencies_installed = True
        # register interface
        register_user_interface()

    except ModuleNotFoundError:
        # Don't register other panels, ui_operators etc.
        print('REGISTRATION FAILED: REQUIRED MODULE NOT FOUND')
        return


def register_user_interface():
    # from ... import cgt_imports
    # cgt_imports.manage_imports(reload=False)

    # print("REGISTER BLENDARMOCAP INTERFACE")
    for cls in get_classes():
        register_class(cls)
    bpy.types.Scene.m_cgtinker_mediapipe = PointerProperty(type=ui_properties.CgtProperties)


def unregister():
    print("Unregister BlendArMocap")
    for cls in get_preferences():
        unregister_class(cls)

    if install_dependencies.dependencies_installed:
        # print("UNREGISTER BLENDARMOCAP WITH ACTIVE DEPENDENCIES")
        classes = get_classes()
        for cls in reversed(classes):
            unregister_class(cls)

        del bpy.types.Scene.m_cgtinker_mediapipe # noqa


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
