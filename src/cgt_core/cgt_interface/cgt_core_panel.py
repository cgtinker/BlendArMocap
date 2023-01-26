import bpy
from .. import cgt_naming
from pathlib import Path


addon_dir_name = None
if addon_dir_name is None:
    f = __file__
    addon_dir_name = Path(f).parent.parent.parent.parent.stem


class DefaultPanel:
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlendAR"
    # bl_options = {"DEFAULT_CLOSED"}
    bl_options = {"HEADER_LAYOUT_EXPAND"}


class PT_UI_CGT_Panel(DefaultPanel, bpy.types.Panel):
    bl_label = cgt_naming.ADDON_NAME
    bl_idname = "UI_PT_CGT_Panel"

    def draw(self, context):
        pass


addon_prefs = set()
class APT_UI_CGT_Panel(bpy.types.AddonPreferences):
    bl_label = cgt_naming.ADDON_NAME
    bl_idname = addon_dir_name

    def draw(self, context):
        global addon_prefs
        for func in addon_prefs:
            func(self, context)


classes = [
    PT_UI_CGT_Panel,
    APT_UI_CGT_Panel,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
