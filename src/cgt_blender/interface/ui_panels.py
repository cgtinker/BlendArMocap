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
        # bridge
        conn_box = self.layout.box()
        conn_box.label(text='Connect')
        if user.connection_operator_running:
            conn_box.row().operator("wm.cgt_local_connection_listener", text="Connected")
        else:
            conn_box.row().operator("wm.cgt_local_connection_listener", text="Start Connection")


        anim_box = self.layout.box()
        anim_box.label(text='Animation Transfer')
        anim_box.row().prop_search(data=user,
                                   property="selected_driver_collection",
                                   search_data=bpy.data,
                                   search_property="collections",
                                   text="Collection",)
        # searching for custom ui prop
        anim_box.row().prop_search(data=user,
                                   property="selected_rig",
                                   search_data=bpy.data,
                                   search_property="objects",
                                   text="Armature",
                                   icon="ARMATURE_DATA")

        anim_box.row().prop(user, "overwrite_drivers_bool")
        anim_box.row().prop(user, "experimental_feature_bool")  # , icon="ERROR")
        anim_box.row().operator("button.cgt_transfer_animation_button", text=user.button_transfer_animation)



class UI_PT_CGT_legacy_detection_panel(DefaultPanel, Panel):
    bl_label = "Legacy Detection"
    bl_idname = "OBJECT_PT_cgt_legacy_detection_panel"
    bl_parent_id = "OBJECT_PT_cgt_main_panel"

    @classmethod
    def poll(cls, context):
        if context.mode in {'OBJECT', 'POSE'}:
            return dependencies.dependencies_installed

    def draw(self, context):
        user = context.scene.m_cgtinker_mediapipe  # noqa

        # detection
        self.layout.prop(user, "detection_input_type")

        if user.detection_input_type == "movie":
            self.layout.prop(user, "mov_data_path")
        else:
            self.layout.prop(user, "webcam_input_device")
            self.layout.prop(user, "key_frame_step")

        # settings
        self.layout.prop(user, "enum_detection_type")
        if user.detection_operator_running:
            self.layout.operator("wm.cgt_feature_detection_operator", text="Stop Detection")
        else:
            self.layout.operator("wm.cgt_feature_detection_operator", text="Start Detection")


class UI_PT_CGT_RemappingPanel(DefaultPanel, Panel):
    bl_label = "Animation Transfer"
    bl_idname = "OBJECT_PT_cgt_remapping_panel"
    bl_parent_id = "OBJECT_PT_cgt_main_panel"

    @classmethod
    def poll(cls, context):
        if context.mode in {'OBJECT', 'POSE'}:
            return dependencies.dependencies_installed

    def draw(self, context):
        user = context.scene.m_cgtinker_mediapipe  # noqa
        # transfer animation

        # self.layout.label(text='Animation Transfer')
        self.layout.prop_search(data=user,
                                property="selected_driver_collection",
                                search_data=bpy.data,
                                search_property="collections",
                                text="")
        # searching for custom ui prop
        self.layout.prop_search(data=user,
                                property="selected_rig",
                                search_data=bpy.data,
                                search_property="objects",
                                text="Armature",
                                icon="ARMATURE_DATA")

        self.layout.prop(user, "overwrite_drivers_bool")
        if user.enum_detection_type in {"POSE", "HOLISTIC"}:
            self.layout.prop(user, "experimental_feature_bool")  # , icon="ERROR")
        self.layout.operator("button.cgt_transfer_animation_button", text=user.button_transfer_animation)


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
