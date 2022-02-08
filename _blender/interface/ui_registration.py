#import importlib

import bpy
from bpy.props import PointerProperty
from bpy.utils import register_class, unregister_class

from _blender.interface import properties, ui_panels, install_dependencies, ui_preferences, \
    stream_detection_operator
#from utils import log

#importlib.reload(ui_panels)
#importlib.reload(properties)
#importlib.reload(ui_preferences)
#importlib.reload(install_dependencies)
#importlib.reload(log)
#importlib.reload(stream_detection_operator)


def get_classes():
    # getting classes to avoid loading possibly unavailable packages
    classes = (
        properties.MyProperties,

        ui_panels.UI_transfer_anim_button,
        stream_detection_operator.WM_modal_detection_operator,

        ui_panels.UI_PT_main_panel
    )
    return classes


def get_preferences():
    preference_classes = (ui_preferences.PREFERENCES_OT_install_dependencies_button,
                          ui_preferences.BLENDARMOCAP_preferences,
                          ui_panels.UI_PT_warning_panel)
    return preference_classes


def register():
    print('REGISTERING BLENDARMOCAP')

    for m_class in get_preferences():
        register_class(m_class)

    try:
        print('TRY ACCESS INSTALLED DEPENDENCIES')
        for dependency in install_dependencies.dependencies:
            print(str(dependency))
            install_dependencies.import_module(module_name=dependency.module, global_name=dependency.name)
        install_dependencies.dependencies_installed = True
        # register interface
        register_user_interface()

    except ModuleNotFoundError:
        # Don't register other panels, ui_operators etc.
        print('REGISTRATION FAILED: MODULE NOT FOUND')
        return


def register_user_interface():
    print("REGISTER BLENDARMOCAP INTERFACE")
    for cls in get_classes():
        register_class(cls)
    bpy.types.Scene.m_cgtinker_mediapipe = PointerProperty(type=properties.MyProperties)


def unregister():
    print("UNREGISTER BLENDARMOCAP")
    for cls in get_preferences():
        unregister_class(cls)

    if install_dependencies.dependencies_installed:
        print("UNREGISTER BLENDARMOCAP WITH ACTIVE DEPENDENCIES")
        classes = get_classes()
        for cls in reversed(classes):
            unregister_class(cls)

        del bpy.types.Scene.m_cgtinker_mediapipe


def manual_unregistration():
    print("UNREGISTER")
    classes = get_classes()
    for cls in reversed(classes):
        unregister_class(cls)

    del bpy.types.Scene.m_cgtinker_mediapipe


def manual_test_registration():
    print("REGISTER")
    for cls in get_classes():
        register_class(cls)
    bpy.types.Scene.m_cgtinker_mediapipe = PointerProperty(type=properties.MyProperties)
