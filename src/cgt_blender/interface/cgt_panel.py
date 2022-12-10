import bpy


class CGT_PT_View3D_Panel(bpy.types.Panel):
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlendAR"
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        if context.mode in {'OBJECT', 'POSE'}:
            return True


class ExpandedPanel:
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlendAR"
    # bl_context = "objectmode"
    bl_options = {"HEADER_LAYOUT_EXPAND"}
