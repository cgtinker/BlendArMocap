# from .cgt_freemocap import fm_registration
from .cgt_core.cgt_interface import cgt_core_registration
from .cgt_mediapipe import cgt_mp_registration
from .cgt_core.cgt_transfer import cgt_transfer_registration
from .cgt_freemocap import fm_registration

""" 
BlendArMocap is split into separated modules. 
Every module has to be registered to be active.
"""


modules = [
    cgt_core_registration,
    cgt_mp_registration,
    fm_registration,
    cgt_transfer_registration,
]


def register():
    for module in modules:
        module.register()


def unregister():
    for module in modules:
        module.unregister()


"""
from cgt_blender.interface import ui_panels
from bpy.props import PointerProperty
from bpy.utils import register_class, unregister_class

# from . import ui_properties, ui_panels, pref_operators, pref_panels, ui_operators


classes = (
    pref_operators.PREFERENCES_OT_CGT_install_dependencies_button,
    pref_operators.PREFERENCES_OT_CGT_uninstall_dependencies_button,
    pref_panels.BLENDARMOCAP_CGT_preferences,

    ui_properties.CGTProperties,

    ui_operators.UI_CGT_transfer_anim_button,
    ui_operators.UI_CGT_toggle_drivers_button,
    ui_operators.UI_CGT_smooth_empties_in_col,
    ui_operators.WM_CGT_modal_detection_operator,
    ui_operators.WM_CGT_modal_connection_listener_operator,
    ui_panels.UI_PT_Detection_Panel,
    ui_panels.UI_PT_CGT_Transfer_Panel
    # ui_panels.UI_PT_RemappingPanel
)


def register():
    print('Registing BlendArMocap\n')
    for _class in classes:
        register_class(_class)

    bpy.types.Scene.m_cgtinker_mediapipe = PointerProperty(type=ui_properties.CGTProperties)


def unregister():
    print("Unregister BlendArMocap")
    for cls in classes:
        try:
            unregister_class(cls)
        except RuntimeError:
            # Class may not be registered
            pass


"""