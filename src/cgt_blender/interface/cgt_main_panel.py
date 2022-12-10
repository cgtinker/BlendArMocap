import bpy
from bpy.types import Panel
from ... import cgt_naming


class DefaultPanel:
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlendAR"
    bl_options = {"DEFAULT_CLOSED"}  # "HEADER_LAYOUT_EXPAND"


class UI_PT_cgt_main_panel(DefaultPanel, Panel):
    bl_label = cgt_naming.ADDON_NAME
    bl_idname = "OBJECT_PT_cgt_main_panel"

    def draw(self, context):
        pass


def register():
    bpy.utils.register_class(UI_PT_cgt_main_panel)


def unregister():
    bpy.utils.unregister_class(UI_PT_cgt_main_panel)
