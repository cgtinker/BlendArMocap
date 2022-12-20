import bpy
from bpy.types import Panel
from .. import cgt_naming


class DefaultPanel:
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlendAR"
    # bl_options = {"DEFAULT_CLOSED"}
    bl_options = {"HEADER_LAYOUT_EXPAND"}


class PT_UI_CGT_Panel(DefaultPanel, Panel):
    bl_label = cgt_naming.ADDON_NAME
    bl_idname = "UI_PT_CGT_Panel"

    def draw(self, context):
        pass


class APT_UI_CGT_Panel(bpy.types.AddonPreferences):
    bl_label = cgt_naming.ADDON_NAME
    bl_idname = "BlendArMocap"

    def draw(self, context):
        layout = self.layout
        box = layout.box()

        box.label(text='Lin ig.')


def register():
    bpy.utils.register_class(APT_UI_CGT_Panel)
    bpy.utils.register_class(PT_UI_CGT_Panel)


def unregister():
    bpy.utils.unregister_class(PT_UI_CGT_Panel)
    bpy.utils.unregister_class(APT_UI_CGT_Panel)
