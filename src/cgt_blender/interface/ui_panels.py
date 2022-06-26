'''
Copyright (C) cgtinker, cgtinker.com, hello@cgtinker.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

from tracemalloc import start
import bpy
from bpy.types import Panel

from . import pref_operators
from ..utils import dependencies
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


class UI_PT_CGT_main_panel(DefaultPanel, Panel):
    bl_label = cgt_naming.ADDON_NAME
    bl_idname = "OBJECT_PT_cgt_main_panel"

    @classmethod
    def poll(cls, context):
        if context.mode in {'OBJECT', 'POSE'}:
            return dependencies.dependencies_installed

    def draw(self, context):
        user = context.scene.m_cgtinker_mediapipe  # noqa

        # detection
        box = self.layout.box()
        box.label(text='Detect')
        if user.pvb:
            box.row().prop(user, "detection_input_type")

        if user.detection_input_type == "movie":
            box.row().prop(user, "mov_data_path")
            start_button_text = user.button_start_detection
        elif user.detection_input_type == "stream":
            box.row().prop(user, "webcam_input_device")
            box.row().prop(user, "key_frame_step")
            start_button_text = user.button_start_detection
        elif user.detection_input_type == "freemocap":
            box.row().prop(user, "freemocap_session_path")
            start_button_text = 'Load `freemocap` data'

        # settings
        box.row().prop(user, "enum_detection_type")
        if user.detection_operator_running:
            box.row().operator("wm.cgt_feature_detection_operator", text="Stop Detection")
        else:
            box.row().operator("wm.cgt_feature_detection_operator", text=start_button_text)

        if user.detection_input_type == "freemocap":
            box.row().operator("wm.fmc_bind_freemocap_data_to_skeleton", text="bind animation to skreleton")
            box.row().operator("wm.fmc_load_synchronized_videos", text="load synchronized videos")

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

        box.row().prop(user, "overwrite_drivers_bool")
        if user.enum_detection_type in {"POSE", "HOLISTIC"}:
            box.row().prop(user, "experimental_feature_bool")  # , icon="ERROR")
        box.row(align=True).operator("button.cgt_transfer_animation_button", text=user.button_transfer_animation)


class UI_PT_CGT_RemappingPanel(DefaultPanel, Panel):
    bl_label = "Utils"
    bl_idname = "OBJECT_PT_cgt_remapping_panel"
    bl_parent_id = "OBJECT_PT_cgt_main_panel"

    @classmethod
    def poll(cls, context):
        if context.mode in {'OBJECT', 'POSE'}:
            return dependencies.dependencies_installed

    def draw(self, context):
        user = context.scene.m_cgtinker_mediapipe  # noqa
        self.layout.use_property_decorate = True  # No animation.

        # detection
        box = self.layout.box()
        box.label(text='Remapping')
        if user.toggle_drivers_bool:
            box.row(align=True).operator("button.cgt_toggle_drivers_button", depress=True)
        else:
            box.row(align=True).operator("button.cgt_toggle_drivers_button", depress=False)
        # box.row().prop(user, "toggle_drivers_bool", icon="CON_ARMATURE")


class UI_PT_CGT_warning_panel(DefaultPanel, Panel):
    bl_label = cgt_naming.ADDON_NAME
    bl_idname = "OBJECT_PT_warning_panel"

    @classmethod
    def poll(self, context):
        return not dependencies.dependencies_installed

    def draw(self, context):
        layout = self.layout

        lines = [f"Please install the missing dependencies for \"{cgt_naming.ADDON_NAME}\".",
                 f"1. Open the preferences (Edit > Preferences > Add-ons).",
                 f"2. Search for the \"{cgt_naming.ADDON_NAME}\" add-on.",
                 f"3. Open the details section of the add-on.",
                 f"4. Click on the \"{pref_operators.PREFERENCES_OT_CGT_install_dependencies_button.bl_label}\" button.",
                 f"   This will download and install the missing Python packages, if Blender has the required",
                 f"   permissions."]

        for line in lines:
            layout.label(text=line)
