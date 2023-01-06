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
import numpy as np

from ...cgt_bpy import cgt_collection
from ...cgt_naming import COLLECTIONS
from ...cgt_utils import cgt_math
from .. import transfer_management


# region TRANSFER
class OT_UI_CGT_transfer_anim_button(bpy.types.Operator):
    bl_label = "Transfer Animation"
    bl_idname = "button.cgt_transfer_animation_button"
    bl_description = "Transfer driver animation to cgt_rig"

    @classmethod
    def poll(cls, context):
        return context.mode in {'OBJECT'}

    def execute(self, context):
        # TODO: APPLY FIX HERE
        from ..cgt_core_transfer import rigify_pose, rigify_face, rigify_fingers

        col_mapping = {
            COLLECTIONS.drivers: 0,
            COLLECTIONS.hands: 0,
            COLLECTIONS.face:  0,
            COLLECTIONS.pose:  0,
        }

        user = bpy.context.scene.cgtinker_rigify_transfer

        selected_driver_collection = user.selected_driver_collection.name
        selected_armature = user.selected_rig.name_full

        print(f"TRYING TO TRANSFER ANIMATION DATA FROM {selected_driver_collection} TO {selected_armature}")

        driver_collections = cgt_collection.get_child_collections(selected_driver_collection)
        for col in driver_collections:

            armature = bpy.data.objects[selected_armature]
            driver_objects =cgt_collection.get_objects_from_collection(col)
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
        # TODO: CHECK, should still work
        # safe current area, switching to graph editor area
        current_area = bpy.context.area.type
        layer = bpy.context.view_layer

        # get objs from selected cols
        user = bpy.context.scene.cgtinker_rigify_transfer
        selected_driver_collection = user.selected_driver_collection.name
        driver_collections = cgt_collection.get_child_collections(selected_driver_collection)
        objs = []
        for col in driver_collections:
            objs += cgt_collection.get_objects_from_collection(col)

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
        # TODO: CHECK: should will work
        user = bpy.context.scene.cgtinker_rigify_transfer
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


class OT_CGT_ObjectMinMax(bpy.types.Operator):
    bl_label = "Object MinMax-fCurve"
    bl_idname = "button.cgt_object_fcurve_min_max"
    bl_description = "Get minimum and maximum values from objects fCurves."

    @classmethod
    def poll(cls, context):
        return context.mode in {'OBJECT'}

    def get_minmax_dist(self, a, b):
        loc_a, *_ = self.get_minmax_transforms(a, True, True, True)
        loc_b, *_ = self.get_minmax_transforms(b, True, True, True)

        if not any(loc_a) and any(loc_b):
            return 0.0, 0.0

        a_min, a_max = loc_a
        b_min, b_max = loc_b

        dists = [
            cgt_math.get_vector_distance(np.array(a_min), np.array(b_min)),
            cgt_math.get_vector_distance(np.array(a_min), np.array(b_max)),
            cgt_math.get_vector_distance(np.array(a_max), np.array(b_min)),
            cgt_math.get_vector_distance(np.array(a_max), np.array(b_max))
        ]

        return min(dists), max(dists)

    def get_minmax_transforms(self, ob, use_loc=True, use_rot=True, use_sca=True):
        loc = [[None, None, None], [None, None, None]]
        rot = [[None, None, None], [None, None, None]]
        sca = [[None, None, None], [None, None, None]]

        if ob.animation_data is None or (ob.animation_data.action is None):
            return loc, rot, sca

        fcurves = ob.animation_data.action.fcurves
        for i, fc in enumerate(fcurves):
            vals = [c.co[1] for c in fc.keyframe_points]

            if fc.data_path == 'location' and use_loc:
                loc[0][i % 3] = min(vals)
                loc[1][i % 3] = max(vals)

            elif fc.data_path == 'scale' and use_sca:
                sca[0][i % 3] = min(vals)
                sca[1][i % 3] = max(vals)

            elif fc.data_path == 'rotation_euler' and use_rot:
                rot[0][i % 3] = min(vals)
                rot[1][i % 3] = max(vals)

        return loc, rot, sca

    def execute(self, context: bpy.context):
        ob = context.object
        if not ob:
            self.report({'ERROR'}, "Ensure to select an object.")
            return {'CANCELED'}

        msg = [ob.name, ':']

        loc, rot, sca = self.get_minmax_transforms(ob, True, True, True)
        for data, name in zip([loc, rot, sca], ['loc', 'rot', 'sca']):
            _min, _max = data
            if not any(_min) and not any(_max):
                continue
            msg.append(f"\n{name}: min {[round(m, 5) for m in _min]}, max {[round(m, 5) for m in _max]}")

        if ob.cgt_props.from_obj is not None and ob.cgt_props.to_obj is not None:
            min_dist, max_dist = self.get_minmax_dist(ob.cgt_props.from_obj, ob.cgt_props.to_obj)
            msg.append(f"\nDist from {ob.cgt_props.from_obj.name} to {ob.cgt_props.to_obj.name}: "
                       f"\nmin: {round(min_dist, 5)} max: {round(max_dist, 5)}\n")

        if ob.cgt_props.remap_from_obj is not None and ob.cgt_props.remap_to_obj is not None:
            min_dist, max_dist = self.get_minmax_dist(ob.cgt_props.remap_from_obj, ob.cgt_props.remap_to_obj)
            msg.append(f"\nDist from {ob.cgt_props.remap_from_obj.name} to {ob.cgt_props.remap_to_obj.name}: "
                       f"\nmin: {round(min_dist, 5)}, max: {round(max_dist, 5)}")

        self.report({'INFO'}, "".join(msg))
        return {'FINISHED'}

    def old_execute(self, context: bpy.context):
        if not context.object:
            self.report({'ERROR'}, "Ensure to select an object.")
            return {'CANCELED'}

        ob = context.object
        d = {
            "location":       "loc",
            "rotation_euler": "rot",
            "scale":          "sca",
            "quaternion":     "qua",
        }

        if ob.animation_data is None or (ob.animation_data.action is None):
            self.report({'WARNING'}, f"{ob.name} doesn't contain any action.")
            return {'CANCELED'}

        msg = [ob.name]
        fcurves = ob.animation_data.action.fcurves
        prev_path = None

        # min&max loc, rot, sca
        for i, fc in enumerate(fcurves):
            vals = [c.co[1] for c in fc.keyframe_points]

            if fc.data_path != prev_path:
                if prev_path is not None:
                    msg.append("\n")
                prev_path = fc.data_path

            s = f"{d[fc.data_path]}[{i % 3}]: min: {round(min(vals), 5)}, max: {round(max(vals), 5)}\n"
            msg.append(s)

        self.report({'INFO'}, "".join(msg))
        return {'FINISHED'}


class OT_CGT_TransferObjectProperties(bpy.types.Operator):
    bl_label = "Transfer from selected"
    bl_idname = "button.cgt_object_transfer_selection"
    bl_description = "Transfer properties from selected objects by generating drivers and populating constraints."

    @classmethod
    def poll(cls, context):
        return context.mode in {'OBJECT'}

    def execute(self, context):
        transfer_management.main(context.selected_objects)
        return {'FINISHED'}

# endregion


classes = [
    OT_UI_CGT_transfer_anim_button,
    OT_UI_CGT_smooth_empties_in_col,
    OT_CGT_Gamerig,
    OT_CGT_ObjectMinMax,
    OT_CGT_TransferObjectProperties,
    # OT_CGT_RegenerateMetarig,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
