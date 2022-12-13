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
from . import cgt_main_panel
from ..utils import dependencies


class PT_CGT_Main_Transfer(cgt_main_panel.DefaultPanel, Panel):
    bl_label = "Transfer"
    bl_parent_id = "UI_PT_CGT_Panel"
    bl_idname = "UI_PT_Transfer_Panel"

    @classmethod
    def poll(cls, context):
        if context.mode in {'OBJECT', 'POSE'}:
            return True

    def draw(self, context):
        pass


class PT_CGT_Data_Transfer(cgt_main_panel.DefaultPanel, Panel):
    bl_label = "Mocap Transfer"
    bl_parent_id = "UI_PT_Transfer_Panel"
    bl_idname = "UI_PT_Transfer_Data"

    def draw(self, context):
        user = context.scene.m_cgtinker_mediapipe  # noqa
        box = self.layout.box()

        box.label(text='Link Mocap data to a generated humanoid rigify rig.')
        box.row(align=True).prop_search(data=user,
                                        property="selected_driver_collection",
                                        search_data=bpy.data,
                                        search_property="collections",
                                        text="Collection")
        # searching for custom ui prop
        box.row(align=True).prop_search(data=user,
                                        property="selected_rig",
                                        search_data=bpy.data,
                                        search_property="objects",
                                        text="Armature",
                                        icon="ARMATURE_DATA")

        # box.row().prop(user, "overwrite_drivers_bool")
        if user.selected_driver_collection:
            if user.selected_driver_collection.name == "cgt_POSE":
                box.row().prop(user, "experimental_feature_bool")  # , icon="ERROR")
            if user.selected_rig:
                box.row(align=True).operator("button.cgt_transfer_animation_button", text="Transfer Animation")
            box.row(align=True).operator("button.smooth_empties_in_col", text="Smooth Animation")


class PT_CGT_Gamerig_Transfer(cgt_main_panel.DefaultPanel, Panel):
    bl_label = "Gamerig Tools"
    bl_parent_id = "UI_PT_Transfer_Panel"
    bl_idname = "UI_PT_Transfer_Gamerig"

    def draw(self, context):
        user = context.scene.m_cgtinker_mediapipe  # noqa
        box = self.layout.box()
        box.label(text='Link Rigify Rig animation to Metarig')
        box.row(align=True).prop_search(data=user,
                                        property="selected_rig",
                                        search_data=bpy.data,
                                        search_property="objects",
                                        text="Generated Rig",
                                        icon="ARMATURE_DATA")

        box.row(align=True).prop_search(data=user,
                                        property="selected_metarig",
                                        search_data=bpy.data,
                                        search_property="objects",
                                        text="Metarig",
                                        icon="ARMATURE_DATA")

        # box.row().operator("button.cgt_regenerate_metarig", text="Regenerate Metarig")
        box.row().operator("button.cgt_generate_gamerig", text="Metarig2Gamerig")


class UI_PT_Panel_Detection(cgt_main_panel.DefaultPanel, Panel):
    bl_label = "Mediapipe"
    bl_parent_id = "UI_PT_CGT_Panel"

    @classmethod
    def poll(cls, context):
        if context.mode in {'OBJECT', 'POSE'} and dependencies.dependencies_installed:
            return True

    def draw(self, context):
        user = context.scene.m_cgtinker_mediapipe  # noqa
        box = self.layout.box()
        box.label(text='Detect')
        box.row().prop(user, "detection_input_type")

        if user.detection_input_type == "movie":
            box.row().prop(user, "mov_data_path")
        else:
            box.row().prop(user, "webcam_input_device")
            box.row().prop(user, "key_frame_step")

        box.row().prop(user, "enum_detection_type")
        if user.modal_active:
            box.row().operator("wm.cgt_feature_detection_operator", text="Stop Detection")
        else:
            box.row().operator("wm.cgt_feature_detection_operator", text="Start Detection")


class UI_PT_CGT_warning_panel(cgt_main_panel.DefaultPanel, Panel):
     bl_label = "CGT_WARN"
     bl_idname = "OBJECT_PT_warning_panel"

     @classmethod
     def poll(self, context):
         return not dependencies.dependencies_installed

     def draw(self, context):
         layout = self.layout

         lines = [f"Please install the missing dependencies for BlendArMocap.",
                  f"1. Open the preferences (Edit > Preferences > Add-ons).",
                  f"2. Search for the BlendArMocap add-on.",
                  f"3. Open the details section of the add-on.",
                  f"4. Click on the 'install dependencies' button.",
                  f"   This will download and install the missing Python packages, if Blender has the required",
                  f"   permissions."]

         for line in lines:
             layout.label(text=line)


classes = [
    UI_PT_Panel_Detection,
    PT_CGT_Main_Transfer,
    PT_CGT_Data_Transfer,
    PT_CGT_Gamerig_Transfer,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
