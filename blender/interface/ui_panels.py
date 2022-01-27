import importlib

import bpy
from bpy.types import Panel

from blender.interface import install_dependencies
from blender.interface import ui_preferences
import CONST

importlib.reload(CONST)
importlib.reload(install_dependencies)
importlib.reload(ui_preferences)


class DefaultPanel:
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = CONST.ADDON_NAME
    bl_context = "objectmode"
    bl_options = {"DEFAULT_CLOSED"}


class ExpandedPanel:
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"
    bl_category = CONST.ADDON_NAME
    bl_context = "objectmode"
    bl_options = {"HEADER_LAYOUT_EXPAND"}


class UI_PT_main_panel(ExpandedPanel, Panel):
    bl_label = CONST.ADDON_NAME
    bl_idname = "OBJECT_PT_main_panel"

    def draw(self, context):
        user = context.scene.m_cgtinker_mediapipe

        # detection
        box = self.layout.box()
        box.label(text='Detect')
        box.row().prop(user, "webcam_input_device")
        box.row().prop(user, "key_frame_step")
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


class UI_PT_warning_panel(ExpandedPanel, Panel):
    bl_label = CONST.ADDON_NAME
    bl_idname = "OBJECT_PT_warning_panel"

    @classmethod
    def poll(self, context):
        return not install_dependencies.dependencies_installed

    def draw(self, context):
        layout = self.layout

        lines = [f"Please install the missing dependencies for \"{CONST.ADDON_NAME}\".",
                 f"1. Open the preferences (Edit > Preferences > Add-ons).",
                 f"2. Search for the \"{CONST.ADDON_NAME}\" add-on.",
                 f"3. Open the details section of the add-on.",
                 f"4. Click on the \"{ui_preferences.PREFERENCES_OT_install_dependencies_button.bl_label}\" button.",
                 f"   This will download and install the missing Python packages, if Blender has the required",
                 f"   permissions."]

        for line in lines:
            layout.label(text=line)
