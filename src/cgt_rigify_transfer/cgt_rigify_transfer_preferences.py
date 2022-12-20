
import bpy
from ..cgt_core.cgt_interface import cgt_core_panel


class UI_APT_CGT_RigifyTransfer(bpy.types.AddonPreferences):
    bl_label = "Rigify Transfer Settings"
    bl_parent_id = "BlendArMocap"
    bl_idname = "PT_APT_CGT_RigifyTransfer"
    # bl_idname = "APT_UI_CGT_RigifyTransferPreferences"

    def draw(self, context):
        preferences = context.preferences
        print("drawing?")
        layout = preferences.layout
        box = layout.box()

        box.label(text='Linssss ig.')

def register():
    print("called", __package__)
    bpy.utils.register_class(UI_APT_CGT_RigifyTransfer)


def unregister():
    bpy.utils.unregister_class(UI_APT_CGT_RigifyTransfer)
