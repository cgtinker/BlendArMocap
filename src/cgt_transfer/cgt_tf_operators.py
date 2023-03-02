import logging
import bpy
from math import degrees
from pathlib import Path
import numpy as np

from .core_transfer import tf_save_object_properties, tf_load_object_properties, tf_transfer_management
from ..cgt_core.cgt_calculators_nodes import cgt_math


# region TRANSFER
class OT_UI_CGT_smooth_empties(bpy.types.Operator):
    bl_label = "Smooth"
    bl_idname = "button.smooth_selected_empties"
    bl_description = "Smooth animation data of selected objects."
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.mode in {'OBJECT'}

    def execute(self, context):
        objs = context.selected_objects
        if len(objs) == 0:
            logging.error("No objects selected when pressing smooth empties button.")
            return {"CANCELED"}

        # safe current area, switching to graph editor area
        current_area = bpy.context.area.type
        layer = bpy.context.view_layer

        for ob in objs:
            ob.select_set(True)
        layer.update()

        bpy.context.area.type = 'GRAPH_EDITOR'
        try:
            bpy.ops.graph.euler_filter()
            bpy.ops.graph.sample()
            bpy.ops.graph.smooth()
        except RuntimeError:
            logging.warning('Selection may not contain animation data to smooth.')
            pass

        bpy.context.area.type = current_area
        for ob in objs:
            ob.select_set(False)
        layer.update()
        layer.update()

        self.report({'INFO'}, f"Smoothed {len(objs)} object animations.")
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
        user = bpy.context.scene.cgtinker_transfer
        if not user.selected_rig:
            logging.error("Ensure to select a generated rig to regenerate it's metarig.")
            return {'CANCELLED'}

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
        return {'FINISHED'}


class OT_CGT_ObjectMinMax(bpy.types.Operator):
    bl_label = "Object MinMax-fCurve"
    bl_idname = "button.cgt_object_fcurve_min_max"
    bl_description = "Get minimum and maximum values from objects fCurves."
    bl_options = {"REGISTER"}

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
            if not vals:
                continue

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
            return {'CANCELLED'}

        msg = [ob.name, ':']

        loc, rot, sca = self.get_minmax_transforms(ob, True, True, True)
        for data, name in zip([loc, rot, sca], ['loc', 'rot', 'sca']):
            _min, _max = data
            if not any(_min) and not any(_max):
                continue
            if name == 'rot':
                msg.append(f"\n{name} in radians: "
                           f"min {[round(m, 5) for m in _min]}, "
                           f"max {[round(m, 5) for m in _max]}")

                msg.append(f"\n{name} in degrees: "
                           f"min {[round(degrees(m), 5) for m in _min]}, "
                           f"max {[round(degrees(m), 5) for m in _max]}")

            else:
                msg.append(f"\n{name}: min {[round(m, 5) for m in _min]}, max {[round(m, 5) for m in _max]}")

        a_min_dist, a_max_dist, b_min_dist, b_max_dist = None, None, None, None
        if ob.cgt_props.from_obj is not None and ob.cgt_props.to_obj is not None:
            a_min_dist, a_max_dist = self.get_minmax_dist(ob.cgt_props.from_obj, ob.cgt_props.to_obj)
            msg.append(f"\nDist from {ob.cgt_props.from_obj.name} to {ob.cgt_props.to_obj.name}: "
                       f"\nmin: {round(a_min_dist, 5)} max: {round(a_max_dist, 5)}\n")

        if ob.cgt_props.remap_from_obj is not None and ob.cgt_props.remap_to_obj is not None:
            b_min_dist, b_max_dist = self.get_minmax_dist(ob.cgt_props.remap_from_obj, ob.cgt_props.remap_to_obj)
            msg.append(f"\nDist from {ob.cgt_props.remap_from_obj.name} to {ob.cgt_props.remap_to_obj.name}: "
                       f"\nmin: {round(b_min_dist, 5)}, max: {round(b_max_dist, 5)}\n")

        if all([a_min_dist, a_max_dist, b_min_dist, b_max_dist]):
            msg.append(f"\nMapped results:\nmin: {round(a_min_dist/b_min_dist, 5)}, min: {round(a_max_dist/b_max_dist, 5)}\n")

        self.report({'INFO'}, "".join(msg))
        return {'FINISHED'}


class OT_CGT_TransferObjectProperties(bpy.types.Operator):
    bl_label = "Transfer from selected"
    bl_idname = "button.cgt_object_transfer_selection"
    bl_description = "Transfer properties from selected objects by generating drivers and populating constraints."
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.mode in {'OBJECT'}

    def execute(self, context):
        tf_transfer_management.main(context.selected_objects)
        self.report({'INFO'}, f"Transferred from {len(context.selected_objects)} selected objects.")
        return {'FINISHED'}


class OT_CGT_SaveObjectProperties(bpy.types.Operator):
    bl_label = "Save Transfer Properties"
    bl_idname = "button.cgt_object_save_properties"
    bl_description = "Saves transfer properties from available objects to file."
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return context.mode in {'OBJECT'}

    def execute(self, context):
        user = context.scene.cgtinker_transfer
        s = user.save_object_properties_name

        print(s)
        if s in ['Rigify_Humanoid_DefaultFace_v0.6.1', 'None']:
            self.report({'ERROR'}, "May not overwrite defaults types.")
            return {'CANCELLED'}

        if len(s) < 3:
            self.report({'ERROR'}, "Use a descriptive type name with at least 3 characters.")
            return {'CANCELLED'}

        if any([True if ch in s else False for ch in ['*', '/', '"', "'", '$', '&', '´', '`', '°', '^', '@']]):
            self.report({'ERROR'}, "Type name may not contain special characters.")
            return {'CANCELLED'}

        path = Path(__file__).parent / 'data'
        files = [x for x in path.glob('**/*') if x.is_file()]
        if s in [(str(x.name)[:-5], str(x.name)[:-5], "") for x in files]:
            self.report({'ERROR'}, "Type name already exists.")
            return {'CANCELLED'}

        s += '.json'
        path = Path(__file__).parent / "data" / s
        json_data = tf_save_object_properties.save([ob for ob in bpy.data.objects if ob.get("cgt_id") is not None])
        json_data.save(str(path))

        user.save_object_properties_bool = False
        user.save_object_properties_name = ""
        self.report({'INFO'}, f"Saved file to {str(path)}.")
        return {'FINISHED'}


class OT_CGT_LoadObjectProperties(bpy.types.Operator):
    bl_label = "Load Transfer Properties"
    bl_idname = "button.cgt_object_load_properties"
    bl_description = "Load transfer properties to objects."
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.mode in {'OBJECT'}

    def execute(self, context):
        user = context.scene.cgtinker_transfer  # noqa
        config = user.transfer_types
        armature = user.selected_rig

        if config in ['None', None] or armature is None:
            self.report({'ERROR'}, f"No configuration file or no armature selected.")
            return {'CANCELLED'}

        config += '.json'
        path = Path(__file__).parent / "data" / config

        tf_load_object_properties.load(context.scene.objects, str(path), armature)
        self.report({'INFO'}, f"Loaded properties from {str(path)}.")
        return {'FINISHED'}


class OT_CGT_DeleteObjectProperties(bpy.types.Operator):
    bl_label = "Delete Transfer Properties"
    bl_idname = "button.cgt_object_delete_properties"
    bl_description = "Delete transfer properties file."
    bl_options = {"REGISTER"}

    @classmethod
    def poll(cls, context):
        return context.mode in {'OBJECT'}

    def execute(self, context):
        user = context.scene.cgtinker_transfer  # noqa
        config = user.transfer_types

        if config in ['Rigify_Humanoid_DefaultFace_v0.6.1', 'None', None]:
            self.report({'ERROR'}, "Default transfer type may not be deleted")
            return {'CANCELLED'}

        config += '.json'
        path = Path(__file__).parent / "data" / config
        path.unlink()

        user.delete_object_properties_bool = False
        self.report({'INFO'}, f"Deleted {str(path)}.")
        return {'FINISHED'}


class OT_CGT_ApplyObjectProperties(bpy.types.Operator):
    bl_label = "Apply Transfer Properties"
    bl_idname = "button.cgt_object_apply_properties"
    bl_description = "Apply transfer properties from available objects."
    bl_options = {"REGISTER", "UNDO"}

    @classmethod
    def poll(cls, context):
        return context.mode in {'OBJECT'}

    def execute(self, context):
        user = context.scene.cgtinker_transfer # noqa
        col = user.selected_driver_collection
        if col is None:
            self.report({'ERROR'}, f"No driver collection selected.")
            return {'CANCELLED'}

        bpy.ops.button.cgt_object_load_properties() # noqa

        objects = []

        def get_objects(m_col):
            nonlocal objects
            objects += m_col.objects
            for sub in m_col.children:
                get_objects(sub)

        get_objects(col)
        tf_transfer_management.main(objects)
        context.view_layer.update()
        self.report({'INFO'}, f"Transferred objects from {col.name}.")
        return {'FINISHED'}


# endregion


classes = [
    OT_UI_CGT_smooth_empties,
    OT_CGT_ObjectMinMax,

    OT_CGT_TransferObjectProperties,
    OT_CGT_ApplyObjectProperties,
    OT_CGT_DeleteObjectProperties,
    OT_CGT_LoadObjectProperties,
    OT_CGT_SaveObjectProperties,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)
