import bpy
from . import fm_interface
from . import fm_operators
from . import fm_modal_operaters


classes = [
    fm_modal_operaters.WM_Load_Freemocap_Operator,
    fm_operators.WM_FMC_bind_freemocap_data_to_skeleton,
    fm_operators.WM_FMC_load_synchronized_videos,
    fm_interface.UI_PT_CGT_Panel_Freemocap
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)