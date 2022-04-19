import bpy
from bpy.types import Panel

from . import pref_operators
from ..utils import install_dependencies
from ... import cgt_naming


class DefaultPanel:
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlendAR"
    # bl_context = "objectmode"
    bl_options = {"DEFAULT_CLOSED"}


class ExpandedPanel:
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = "BlendAR"
    # bl_context = "objectmode"
    bl_options = {"HEADER_LAYOUT_EXPAND"}


class UI_PT_main_panel(DefaultPanel, Panel):
    bl_label = cgt_naming.ADDON_NAME
    bl_idname = "OBJECT_PT_cgt_main_panel"

    @classmethod
    def poll(cls, context):
        return context.mode in {'OBJECT', 'POSE'}  # list all the modes you want here

    def draw(self, context):
        user = context.scene.m_cgtinker_mediapipe  # noqa

        # detection
        box = self.layout.box()
        box.label(text='Detect')
        if user.pvb:
            box.row().prop(user, "detection_input_type")

        if user.detection_input_type == "movie":
            box.row().prop(user, "mov_data_path")
        else:
            box.row().prop(user, "webcam_input_device")
            box.row().prop(user, "key_frame_step")

        # settings
        box.row().prop(user, "enum_detection_type")
        if user.detection_operator_running:
            box.row().operator("wm.cgt_feature_detection_operator", text="Stop Detection")
        else:
            box.row().operator("wm.cgt_feature_detection_operator", text=user.button_start_detection)

        # transfer animation
        box = self.layout.box()

        box.label(text='Animation Transfer')
        box.row(align=True).prop_search(data=user,
                                        property="selected_driver_collection",
                                        search_data=bpy.data,
                                        search_property="collections",
                                        text="Drivers")
        # searching for custom ui prop
        box.row(align=True).prop_search(data=user,
                                        property="selected_rig",
                                        search_data=bpy.data,
                                        search_property="objects",
                                        text="Armature",
                                        icon="ARMATURE_DATA")

        if user.enum_detection_type == "POSE":
            box.row().prop(user, "experimental_feature_bool")  # , icon="ERROR")

        box.row(align=True).operator("button.cgt_transfer_animation_button", text=user.button_transfer_animation)


class UI_PT_warning_panel(DefaultPanel, Panel):
    bl_label = cgt_naming.ADDON_NAME
    bl_idname = "OBJECT_PT_warning_panel"

    @classmethod
    def poll(self, context):
        return not install_dependencies.dependencies_installed

    def draw(self, context):
        layout = self.layout

        lines = [f"Please install the missing dependencies for \"{cgt_naming.ADDON_NAME}\".",
                 f"1. Open the preferences (Edit > Preferences > Add-ons).",
                 f"2. Search for the \"{cgt_naming.ADDON_NAME}\" add-on.",
                 f"3. Open the details section of the add-on.",
                 f"4. Click on the \"{pref_operators.PREFERENCES_OT_install_dependencies_button.bl_label}\" button.",
                 f"   This will download and install the missing Python packages, if Blender has the required",
                 f"   permissions."]

        for line in lines:
            layout.label(text=line)
