from __future__ import annotations
import bpy


class OBJECT_PT_BlendArMocapTransfer(bpy.types.Panel):
    # Transfer panel in object constraint space
    bl_label = "BlendArMocap"
    bl_options = {'HEADER_LAYOUT_EXPAND'}
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
    bl_options = {'HEADER_LAYOUT_EXPAND'}
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
    bl_options = {'HEADER_LAYOUT_EXPAND'}
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
            col.separator_spacer()

            # REMAP BY PROPS
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

        elif ob.cgt_props.driver_type == 'REMAP':
            if ob.cgt_props.by_obj.target_type != 'NONE':
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

        elif ob.cgt_props.driver_type == 'REMAP_DIST':
            col.prop(ob.cgt_props, "from_obj", text="Distance From")
            col.prop(ob.cgt_props, "to_obj", text="Distance To")
            col.separator_spacer()

            col.prop(ob.cgt_props, "remap_from_obj", text="Normalize Distance From")
            col.prop(ob.cgt_props, "remap_to_obj", text="Normalize Distance To")
            col.separator_spacer()

            # PROPS
            col.prop(ob.cgt_props.by_obj, "target", text="Remap By")
            col.prop(ob.cgt_props.by_obj, "target_type", text="Multiply MinMax By")

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
        if ob.cgt_props.driver_type in ['REMAP', 'REMAP_DIST']:
            return True
        return False

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

        def draw_sub_props(label, props, details):
            row = col.row(heading=label, align=True)
            row.use_property_decorate = False
            sub = row.row(align=True)

            for prop, name, text in props:
                sub.prop(prop, name, text=text, toggle=True)

            row.label(icon='BLANK1')
            if getattr(ob.cgt_props, details[0], False):
                detailed_properties(['X', 'Y', 'Z'], [prop[0] for prop in props], details[1])
            elif any([prop[0].active for prop in props]):
                draw_props("", props[0][0], details[2])


        loc_props = [
            [ob.cgt_props.use_loc_x, "active", "X"],
            [ob.cgt_props.use_loc_y, "active", "Y"],
            [ob.cgt_props.use_loc_z, "active", "Z"],
            [ob.cgt_props, "loc_details", "+"],
        ]

        rot_props = [
            [ob.cgt_props.use_rot_x, "active", "X"],
            [ob.cgt_props.use_rot_y, "active", "Y"],
            [ob.cgt_props.use_rot_z, "active", "Z"],
            [ob.cgt_props, "rot_details", "+"],
        ]

        sca_props = [
            [ob.cgt_props.use_sca_x, "active", "X"],
            [ob.cgt_props.use_sca_y, "active", "Y"],
            [ob.cgt_props.use_sca_z, "active", "Z"],
            [ob.cgt_props, "sca_details", "+"],
        ]

        if ob.cgt_props.driver_type == 'REMAP':
            draw_sub_props("From Location", loc_props, ("loc_details", "remap_details", "remap_default"))
            draw_sub_props("From Rotation", rot_props, ("rot_details", "remap_details", "remap_default"))

        elif ob.cgt_props.driver_type == 'REMAP_DIST':
            draw_sub_props("To Location", loc_props, ("loc_details", "remap_none", "remap_default"))
            draw_sub_props("To Rotation", rot_props, ("rot_details", "remap_none", "remap_default"))
            draw_sub_props("To Scale", sca_props, ("sca_details", "remap_none", "remap_default"))

        # TODO: consider to implement x,y,z mapping for chain elements in the future
        elif ob.cgt_props.driver_type == 'CHAIN':
            draw_sub_props("To Location", loc_props, ("loc_details", "remap_details", "remap_default"))


class OBJECT_PT_CGT_DriverTools(bpy.types.Panel):
    """ Spy for easier mapping and transfer button"""

    bl_label = "Tools"
    bl_parent_id = "OBJECT_PT_CGT_Transfer_Opts"
    bl_idname = "OBJECT_PT_CGT_DriverTools"
    bl_options = {'DEFAULT_CLOSED'}
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'

    def draw(self, context):
        layout = self.layout
        layout.use_property_split = True
        flow = layout.grid_flow(row_major=True, columns=0, even_columns=True, even_rows=False, align=False)
        col = flow.column(align=True)

        col.row().operator("button.cgt_object_transfer_selection", text="Transfer Selection")
        col.separator()
        col.row().operator("button.smooth_selected_empties", text="Smooth Animation Data of Selection")
        col.separator()
        col.row().operator("button.cgt_object_fcurve_min_max", text="Log Object Info")


classes = [
    OBJECT_PT_BlendArMocapTransfer,
    OBJECT_PT_BlendArMocapTransferTarget,
    OBJECT_PT_CGT_DriverProperties,
    OBJECT_PT_CGT_DriverTools,
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
