import bpy
from bpy.types import Panel


class DefaultPanel:
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlendArMocap"
    bl_context = "objectmode"
    bl_options = {"DEFAULT_CLOSED"}


class ExpandedPanel:
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlendArMocap"
    bl_context = "objectmode"
    bl_options = {"HEADER_LAYOUT_EXPAND"}


class UI_PT_main_panel(ExpandedPanel, Panel):
    bl_label = "BlendArMocap"
    bl_idname = "OBJECT_PT_main_panel"

    def draw(self, context):
        user = context.scene.m_cgtinker_mediapipe

        # detection
        box = self.layout.box()
        box.label(text='Detect')
        box.row().prop(user, "webcam_input_device")
        box.row().prop(user, "enum_detection_type")
        box.row().operator("button.detection_button", text=user.button_start_detection)

        # transfer animation
        box = self.layout.box()

        box.label(text='Animation Transfer')
        box.row(align=True).prop_search(data=user,
                                        property="selected_driver_collection",
                                        search_data=bpy.data,
                                        search_property="collections",
                                        text="Drivers")

        box.row(align=True).prop_search(data=user,
                                        property="selected_rig",
                                        search_data=bpy.data,
                                        search_property="armatures",
                                        text="Armature")

        box.row(align=True).operator("button.transfer_animation", text=user.button_transfer_animation)
