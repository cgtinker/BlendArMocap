import bpy
from . import fm_interface
from . import fm_modal_session_load_operater


classes = [
    fm_modal_session_load_operater.WM_Load_Freemocap_Operator,
    fm_interface.PT_CGT_main_panel
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)