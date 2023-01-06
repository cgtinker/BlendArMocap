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
from ...cgt_interface import cgt_core_panel



import bpy
from bpy.props import PointerProperty


class CgtRigifyTransferProperties(bpy.types.PropertyGroup):
    def is_rigify_armature(self, object):
        if object.type == 'ARMATURE':
            if 'rig_id' in object.data:
                return True
        return False

    transfer_types: bpy.props.EnumProperty(
        name="Target Type",
        items=(
            ("RIGIFY", "Rigify Rig", ""),
            ("OTHER", "Other Rig", ""),
        )
    )
    selected_rig: bpy.props.PointerProperty(
        type=bpy.types.Object,
        description="Select an armature for animation transfer.",
        name="Armature",
        poll=is_rigify_armature)

    def is_armature(self, object):
        if object.type == 'ARMATURE':
            if 'rig_id' in object.data:
                return False
            return True
        return False

    selected_metarig: bpy.props.PointerProperty(
        type=bpy.types.Object,
        description="Select a metarig as future gamerig.",
        name="Armature",
        poll=is_armature)

    def cgt_collection_poll(self, object):
        return object.name.startswith('cgt_')

    selected_driver_collection: bpy.props.PointerProperty(
        name="",
        type=bpy.types.Collection,
        description="Select a collection of Divers.",
        poll=cgt_collection_poll
    )


class PT_CGT_Main_Transfer(cgt_core_panel.DefaultPanel, Panel):
    bl_label = "Transfer"
    bl_parent_id = "UI_PT_CGT_Panel"
    bl_idname = "UI_PT_Transfer_Panel"

    @classmethod
    def poll(cls, context):
        if context.mode in {'OBJECT', 'POSE'}:
            return True

    def draw(self, context):
        user = context.scene.cgtinker_rigify_transfer  # noqa
        box = self.layout.box()

        box.label(text='Link Mocap data to a generated humanoid rigify rig.')
        box.row().prop(user, "transfer_types", text="Transfer Type")
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

        if not user.selected_driver_collection and user.selected_rig:
            return

        box.row(align=True).operator("button.cgt_transfer_animation_button", text="Transfer Animation")


class PT_CGT_Gamerig_Transfer(cgt_core_panel.DefaultPanel, Panel):
    bl_label = "Gamerig Tools"
    bl_parent_id = "UI_PT_Transfer_Panel"
    bl_idname = "UI_PT_Transfer_Gamerig"

    def draw(self, context):
        user = context.scene.cgtinker_rigify_transfer  # noqa
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


class PT_CGT_TransferTypeGeneration(cgt_core_panel.DefaultPanel, Panel):
    bl_label = "Transfer Generation Tools"
    bl_parent_id = "UI_PT_Transfer_Panel"
    bl_idname = "UI_PT_TransferTypeGeneration"

    def draw(self, context):
        user = context.scene.cgtinker_rigify_transfer  # noqa
        box = self.layout.box()
        box.label(text='Link Rigify Rig animation to Metarig')
        box.row(align=True).prop_search(data=user,
                                        property="selected_rig",
                                        search_data=bpy.data,
                                        search_property="objects",
                                        text="New Transfer Type",
                                        icon="ARMATURE_DATA")

        box.row(align=True).prop_search(data=user,
                                        property="selected_metarig",
                                        search_data=bpy.data,
                                        search_property="objects",
                                        text="Test",
                                        icon="ARMATURE_DATA")

        # box.row().operator("button.cgt_regenerate_metarig", text="Regenerate Metarig")
        box.row().operator("button.cgt_generate_gamerig", text="SomeRandomName")

classes = [
    PT_CGT_Main_Transfer,
    CgtRigifyTransferProperties,
    PT_CGT_TransferTypeGeneration,
    PT_CGT_Gamerig_Transfer,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)
    bpy.types.Scene.cgtinker_rigify_transfer = PointerProperty(type=CgtRigifyTransferProperties)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
    del bpy.types.Scene.cgtinker_rigify_transfer
