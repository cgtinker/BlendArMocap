# ##### BEGIN GPL LICENSE BLOCK #####
#
#  This program is free software; you can redistribute it and/or
#  modify it under the terms of the GNU General Public License
#  as published by the Free Software Foundation; either version 2
#  of the License, or (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program; if not, write to the Free Software Foundation,
#  Inc., 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301, USA.
#
# ##### END GPL LICENSE BLOCK #####

# <pep8 compliant>

from __future__ import annotations
import bpy


# TODO: utils -> remove
def get_constraint_props(c: bpy.types.Constraint):
    pool = {'__doc__', 'target', 'subtarget', '__module__', '__slots__', 'is_valid',
            'active', 'bl_rna', 'error_location', 'error_rotation', 'head_tail',
            'is_proxy_local', 'mute', 'rna_type', 'show_expanded', 'use_bbone_shape'}
    props = {key: getattr(c, key, None) for key in dir(c) if key not in pool}
    return props


# TODO: CHECK IF REQUIRED IN ANY WAY. REQ FOR CONSTRAINTS
def get_custom_props(ob: bpy.types.Object):
    pool = {'prop', '_RNA_UI', 'cgt_id', 'cycles', 'cycles_visibility'}
    props = {key: getattr(ob, key, None) for key in ob.keys() if key not in pool}
    return props


class OBJECT_PT_BlendArMocapTransfer(bpy.types.Panel):
    # Transfer panel in object constraint space
    bl_label = "BlendArMocap"
    bl_options = {'DEFAULT_CLOSED'}
    bl_idname = "OBJECT_PT_CGT_Transfer_Opts"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "constraint"

    obj_prop: bpy.props.PointerProperty(type=bpy.types.Object)

    @classmethod
    def poll(self, context):
        # return context.object.cgt_props.active
        if context.object.get("cgt_id") == "11b1fb41-1349-4465-b3aa-78db80e8c761":
            return True
        return False

    def draw(self, context):
        pass


class OBJECT_PT_BlendArMocapTransferTarget(bpy.types.Panel):
    """ Transfer targets may be type of Object, Bone, Shape Key.
        These copy values from drivers preferably using constraints.
        Shape Keys may be driven by the drivers directly. """

    bl_label = "Target"
    bl_parent_id = "OBJECT_PT_CGT_Transfer_Opts"
    bl_options = {'DEFAULT_CLOSED'}
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'

    def draw(self, context):
        # layout
        layout = self.layout
        layout.use_property_split = True
        flow = layout.grid_flow(row_major=True, columns=0, even_columns=True, even_rows=False, align=False)
        col = flow.column()

        # target prop
        ob = context.object
        col.prop(ob.cgt_props.target, "obj_type", text="Target Type")
        col.prop(ob.cgt_props.target, "target", text="Target")

        target_ob = ob.cgt_props.target.target
        if target_ob is None:
            return

        # selection for subtype
        if target_ob.type == 'ARMATURE' and ob.cgt_props.target.obj_type == 'ARMATURE':
            col.prop(ob.cgt_props.target, "armature_type", text="Sub Target")
            if ob.cgt_props.target.armature_type == 'BONE' and len(target_ob.data.bones) > 0:
                col.prop_search(ob.cgt_props.target, "target_bone", target_ob.data, "bones", text="Bone")

        elif target_ob.type == 'MESH' and ob.cgt_props.target.obj_type == 'MESH':
            col.prop(ob.cgt_props.target, "object_type", text="Sub Target")
            if ob.cgt_props.target.object_type == 'SHAPE_KEY' and target_ob.data.shape_keys is not None:
                col.prop_search(ob.cgt_props.target, "target_shape_key", target_ob.data.shape_keys, "key_blocks",
                                text="Shape Key")


class OBJECT_PT_CGT_DriverProperties(bpy.types.Panel):
    """ Driver Properties Panel - allows user to setup drivers for mocap transfer.
        Some different types of drivers are selectable. """

    bl_label = "Drivers"
    bl_parent_id = "OBJECT_PT_CGT_Transfer_Opts"
    bl_idname = "OBJECT_PT_CGT_DriverProperties"
    bl_options = {'DEFAULT_CLOSED'}
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'

    def draw(self, context):
        # layout
        layout = self.layout
        layout.use_property_split = True
        flow = layout.grid_flow(row_major=True, columns=0, even_columns=True, even_rows=False, align=False)
        col = flow.column(align=True)

        ob = context.object
        if ob is None:
            return

        # col.use_property_decorate = False
        col.prop(ob.cgt_props, "driver_type", text="Driver Type")
        col.label(icon='BLANK1')

        col = layout.column()
        if ob.cgt_props.driver_type == 'CHAIN':
            col.prop(ob.cgt_props, "to_obj", text="Parent")

        elif ob.cgt_props.driver_type == 'REMAP':
            pass

        elif ob.cgt_props.driver_type == 'REMAP_DIST':
            col.prop(ob.cgt_props, "to_obj", text="Distance To")
            col.separator_spacer()

            # PROPS
            col.prop(ob.cgt_props.by_obj, "target", text="Remap By")
            col.prop(ob.cgt_props.by_obj, "target_type", text="Remap Type")

            if ob.cgt_props.by_obj.target_type == 'BONE_LEN' and ob.cgt_props.by_obj.target is not None:
                col.prop_search(ob.cgt_props.by_obj, "target_bone", ob.cgt_props.by_obj.target.data, "bones")

            elif ob.cgt_props.by_obj.target_type == 'BONE_DIST' and ob.cgt_props.by_obj.target is not None:
                col.prop_search(ob.cgt_props.by_obj, "target_bone", ob.cgt_props.by_obj.target.data, "bones",
                                text="From Bone")
                col.prop(ob.cgt_props.by_obj, "target_bone_type", text="Type")
                col.prop_search(ob.cgt_props.by_obj, "other_bone", ob.cgt_props.by_obj.target.data, "bones",
                                text="To Bone")
                col.prop(ob.cgt_props.by_obj, "other_bone_type", text="Type")

        else:
            pass


class OBJECT_PT_CGT_DriverPropertyDetails(bpy.types.Panel):
    """ Driver remap property details. """
    bl_label = "Value Mapping"
    bl_parent_id = "OBJECT_PT_CGT_DriverProperties"
    bl_options = {'DEFAULT_CLOSED'}
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'

    @classmethod
    def poll(self, context):
        ob = context.object
        if ob is None:
            return False
        if ob.cgt_props.driver_type in ['PASS_THROUGH', 'CHAIN']:
            return False
        return True

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        flow = layout.grid_flow(row_major=True, columns=0, even_columns=True, even_rows=False, align=False)
        col = flow.column(align=True)

        ob = context.object
        if ob is None:
            return

        def draw_props(identifier, group, remap_type="remap_default"):
            row = col.row(heading=f"{identifier} To Axis", align=True)
            row.use_property_decorate = False
            sub = row.row(align=True)
            sub.prop(group, remap_type, text=f"{identifier} To Axis")
            row.label(icon='BLANK1')

            row = col.row(align=True)
            sub = row.column(align=True)
            sub.prop(group, "from_min", text=f"From Min", toggle=True)
            sub.prop(group, "from_max", text=f"From Max")

            row = col.row(align=True)
            sub = row.column(align=True)
            sub.prop(group, "to_min", text=f"To Min", toggle=True)
            sub.prop(group, "to_max", text=f"To Max")
            col.separator()

            row = col.row(align=True)
            sub = row.column(align=True)
            sub.prop(group, "offset", text=f"Offset", toggle=True)
            sub.prop(group, "factor", text=f"Factor")
            col.separator()

        def detailed_properties(identifieres, groups, remap_type="remap_details"):
            nonlocal ob
            for identifier, group in zip(identifieres, groups):
                if group.active:
                    draw_props(identifier, group, remap_type)

        row = col.row(heading="From Location", align=True)
        row.use_property_decorate = False
        sub = row.row(align=True)
        sub.prop(ob.cgt_props.use_loc_x, "active", text="X", toggle=True)
        sub.prop(ob.cgt_props.use_loc_y, "active", text="Y", toggle=True)
        sub.prop(ob.cgt_props.use_loc_z, "active", text="Z", toggle=True)
        sub.prop(ob.cgt_props, "loc_details", text="+", toggle=True)
        row.label(icon='BLANK1')
        if ob.cgt_props.loc_details:
            detailed_properties(
                ['X', 'Y', 'Z'],
                [ob.cgt_props.use_loc_x, ob.cgt_props.use_loc_y, ob.cgt_props.use_loc_z],
                "remap_details")
        elif any([ob.cgt_props.use_loc_x.active, ob.cgt_props.use_loc_y.active, ob.cgt_props.use_loc_z.active]):
            draw_props("", ob.cgt_props.use_loc_x, "remap_default")

        row = col.row(heading="From Rotation", align=True)
        row.use_property_decorate = False
        sub = row.row(align=True)
        sub.prop(ob.cgt_props.use_rot_x, "active", text="X", toggle=True)
        sub.prop(ob.cgt_props.use_rot_y, "active", text="Y", toggle=True)
        sub.prop(ob.cgt_props.use_rot_z, "active", text="Z", toggle=True)
        sub.prop(ob.cgt_props, "rot_details", text="+", toggle=True)
        row.label(icon='BLANK1')
        if ob.cgt_props.rot_details:
            detailed_properties(
                ['X', 'Y', 'Z'],
                [ob.cgt_props.use_rot_x, ob.cgt_props.use_rot_y, ob.cgt_props.use_rot_z],
                "remap_details")
        elif any([ob.cgt_props.use_rot_x.active, ob.cgt_props.use_rot_y.active, ob.cgt_props.use_rot_z.active]):
            draw_props("", ob.cgt_props.use_rot_x, "remap_default")

        if ob.cgt_props.driver_type != "REMAP_DIST":
            return
        # TODO: Remove? We can use actual distance between objects (even if it's a bit more to calc)
        row = col.row(heading="From Scale", align=True)
        row.use_property_decorate = False
        sub = row.row(align=True)
        sub.prop(ob.cgt_props.use_sca_x, "active", text="Length", toggle=True)
        # sub.prop(ob.cgt_props.use_sca_y, "active", text="Y", toggle=True)
        # sub.prop(ob.cgt_props.use_sca_z, "active", text="Z", toggle=True)
        row.label(icon='BLANK1')


classes = [
    OBJECT_PT_BlendArMocapTransfer,
    OBJECT_PT_BlendArMocapTransferTarget,
    OBJECT_PT_CGT_DriverProperties,
    OBJECT_PT_CGT_DriverPropertyDetails,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)


if __name__ == '__main__':
    unregister()
    register()
