from bpy.types import Panel


class DefaultPanel:
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BpyMediapipe"
    bl_context = "objectmode"
    bl_options = {"DEFAULT_CLOSED"}


class ExpandedPanel:
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BpyMediapipe"
    bl_context = "objectmode"
    bl_options = {"HEADER_LAYOUT_EXPAND"}


class UI_PT_main_panel(ExpandedPanel, Panel):
    bl_label = "BpyMediapipe"
    bl_idname = "OBJECT_PT_main_panel"

    def draw(self, context):
        user = context.scene.m_cgtinker_mediapipe

        box = self.layout.box()
        box.label(text='Detection Properties')
        box.row().prop(user, "webcam_input_device")
        box.row().prop(user, "enum_detection_type")
        box.row().prop(user, "enum_synchronize")

        self.layout.split(factor=2.0, align=False)
        self.layout.operator("button.add_rig", text=user.button_add_rig)
        self.layout.operator("button.detection_button", text=user.button_start_detection)
