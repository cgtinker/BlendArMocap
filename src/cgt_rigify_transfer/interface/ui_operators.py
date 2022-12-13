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

import logging
import bpy

import src.cgt_core.cgt_bpy.cgt_collection
from ...cgt_core.cgt_bpy import objects
from src.cgt_core.cgt_naming import COLLECTIONS


# region TRANSFER
class OT_UI_CGT_transfer_anim_button(bpy.types.Operator):
    bl_label = "Transfer Animation"
    bl_idname = "button.cgt_transfer_animation_button"
    bl_description = "Transfer driver animation to cgt_rig"

    @classmethod
    def poll(cls, context):
        return context.mode in {'OBJECT'}

    def execute(self, context):
        from ..cgt_core_transfer import rigify_pose, rigify_face, rigify_fingers

        col_mapping = {
            COLLECTIONS.hands: rigify_fingers.RigifyHands,
            COLLECTIONS.face:  rigify_face.RigifyFace,
            COLLECTIONS.pose:  rigify_pose.RigifyPose
        }

        user = bpy.context.scene.m_cgtinker_mediapipe

        selected_driver_collection = user.selected_driver_collection.name
        selected_armature = user.selected_rig.name_full

        print(f"TRYING TO TRANSFER ANIMATION DATA FROM {selected_driver_collection} TO {selected_armature}")

        driver_collections = src.cgt_core.cgt_bpy.cgt_collection.get_child_collections(selected_driver_collection)
        for col in driver_collections:

            armature = bpy.data.objects[selected_armature]
            driver_objects = src.cgt_core.cgt_bpy.cgt_collection.get_objects_from_collection(col)
            col_mapping[col](armature, driver_objects)

        # input_manager.transfer_animation()
        return {'FINISHED'}


class OT_UI_CGT_smooth_empties_in_col(bpy.types.Operator):
    bl_label = "Smooth"
    bl_idname = "button.smooth_empties_in_col"
    bl_description = "Smooth the animation data in the selected collection."

    @classmethod
    def poll(cls, context):
        return context.mode in {'OBJECT'}

    def execute(self, context):
        # safe current area, switching to graph editor area
        current_area = bpy.context.area.type
        layer = bpy.context.view_layer

        # get objs from selected cols
        user = bpy.context.scene.m_cgtinker_mediapipe
        selected_driver_collection = user.selected_driver_collection.name
        driver_collections = src.cgt_core.cgt_bpy.cgt_collection.get_child_collections(selected_driver_collection)
        objs = []
        for col in driver_collections:
            objs += src.cgt_core.cgt_bpy.cgt_collection.get_objects_from_collection(col)

        print("selecting objects")
        for ob in objs:
            ob.select_set(True)
        layer.update()

        print("start smoothing process")
        bpy.context.area.type = 'GRAPH_EDITOR'
        bpy.ops.graph.euler_filter()
        bpy.ops.graph.sample()
        bpy.ops.graph.smooth()

        print("process finished")
        bpy.context.area.type = current_area
        for ob in objs:
            ob.select_set(False)
        layer.update()
        layer.update()

        return {'FINISHED'}


class OT_CGT_Gamerig(bpy.types.Operator):
    bl_label = "Rigify to Gamerig"
    bl_idname = "button.cgt_generate_gamerig"
    bl_description = "Transfer the animation from a generated rigify rig to a metarig."

    @classmethod
    def poll(cls, context):
        return context.mode in {'OBJECT'}

    def execute(self, context):
        user = bpy.context.scene.m_cgtinker_mediapipe
        metarig = user.selected_metarig
        rig = user.selected_rig

        d = {}
        if metarig is None:
            logging.warning("No rig to transfer to selected.")
            return {'CANCELED'}

        if rig is None:
            logging.warning("No rig to transfer from selected.")
            return {'CANCELED'}

        for bone in metarig.data.bones:
            d[bone.name] = ''

        rig = bpy.data.objects['rig']
        for bone in rig.data.bones:
            if bone.layers[29] or bone.use_deform:
                name = bone.name
                if name.startswith('DEF-'):
                    name = name.replace('DEF-', '')
                if name not in d:
                    d[name] = None
                else:
                    d[name] = bone.name

        for key, value in d.items():
            if value != None:
                constraint = metarig.pose.bones[key].constraints.new('COPY_TRANSFORMS')
                constraint.target = rig
                constraint.subtarget = value
                constraint.influence = 1

        return {'FINISHED'}


class OT_CGT_RegenerateMetarig(bpy.types.Operator):
    """ TODO: Implement regen """
    bl_label = "Regenerate Metarig"
    bl_idname = "button.cgt_regenerate_metarig"
    bl_description = "Regenerates the metarig from a rigify rig."

    @classmethod
    def poll(cls, context):
        return context.mode in {'OBJECT'}

    def execute(self, context: bpy.context):
        user = bpy.context.scene.m_cgtinker_mediapipe
        if not user.selected_rig:
            logging.error("Ensure to select a generated rig to regenerate it's metarig.")
            return {'CANCELED'}

        bone_data = {}
        source_rig = user.selected_rig.name

        # generate new metarig
        bpy.ops.object.armature_human_metarig_add()
        dest_rig = bpy.context.object.name

        def edit_rig(rigname):
            bpy.ops.object.mode_set(mode='OBJECT')
            bpy.ops.object.select_all(action='DESELECT')
            bpy.data.objects[rigname].select_set(True)
            bpy.context.view_layer.objects.active = bpy.data.objects[rigname]
            bpy.ops.object.mode_set(mode='EDIT')

        # select source rig and copy values
        edit_rig(source_rig)
        for b in bpy.data.objects[source_rig].data.edit_bones:
            bone_data[b.name] = (b.head.copy(), b.tail.copy(), b.roll)

        # apply values to dest rig
        edit_rig(dest_rig)
        for b in bpy.data.objects[dest_rig].data.edit_bones:
            b.head, b.tail, b.roll = bone_data[b.name]

        bpy.ops.object.mode_set(mode='OBJECT')


class OT_UI_CGT_toggle_drivers_button(bpy.types.Operator):
    bl_label = "Toggle Drivers"
    bl_idname = "button.cgt_toggle_drivers_button"
    bl_description = "Toggle drivers to improve performance while motion capturing"
    # TODO: IMPLEMENT PROPER WAY TO TOGGLE

    @classmethod
    def poll(cls, context):
        return context.mode == 'OBJECT'

    def execute(self, context):
        user = bpy.context.scene.m_cgtinker_mediapipe  # noqa
        user.toggle_drivers_bool = not user.toggle_drivers_bool
        print("toggled", user.toggle_drivers_bool)

        driver_collections = src.cgt_core.cgt_bpy.cgt_collection.get_child_collections('CGT_DRIVERS')
        objs = src.cgt_core.cgt_bpy.cgt_collection.get_objects_from_collection('CGT_DRIVERS')
        print(objs)
        return {'FINISHED'}
# endregion



classes = [
    OT_UI_CGT_transfer_anim_button,
    OT_UI_CGT_smooth_empties_in_col,
    OT_CGT_Gamerig,
    # OT_CGT_RegenerateMetarig,
    OT_UI_CGT_toggle_drivers_button,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
