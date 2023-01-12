import bpy
import logging


# region pools and dynamic enums
def pool_transfer_target(self, obj):
    if obj.type == self.obj_type:
        return True
    elif self.obj_type == 'ANY':
        return True
    return False


def get_shape_key_enum(self, context):
    ob = self.target
    if ob is None or ob.type != 'MESH':
        return [('NONE', "None", "")]
    if ob.data.shape_keys is None:
        return [('NONE', "None", "")]
    return [(key.name, key.name, "") for key in ob.data.shape_keys.key_blocks]


def get_bones_enum(self, context):
    items = [('NONE', "None", "")]
    if not hasattr(self, 'target'):
        return items

    obj = self.target
    if hasattr(obj, 'data') and (hasattr(obj.data, 'bones')):
        items += [(bone.name, bone.name, "") for bone in obj.data.bones]
    else:
        return items

    return items


def is_armature(self, obj):
    if obj.type == 'ARMATURE':
        return True
    return False
# endregion


# region sub properties for drivers
class OBJECT_PGT_CGT_TransferTarget(bpy.types.PropertyGroup):
    """ Target for data transfer. """
    obj_type: bpy.props.EnumProperty(
        name="Object Type",
        items=(
            ("ARMATURE", "Armature", ""),
            ("MESH", "Mesh", ""),
            ("ANY", "Any", ""),
        )
    )

    target: bpy.props.PointerProperty(
        type=bpy.types.Object,
        poll=pool_transfer_target,
        description="Select an object for animation transfer.",
    )

    armature_type: bpy.props.EnumProperty(
        name="Target Type",
        items=(
            ("ARMATURE", "Object", ""),
            ("BONE", "Bone", ""),
        )
    )

    object_type: bpy.props.EnumProperty(
        name="Target Type",
        items=(
            ("OBJECT", "Object", ""),
            # ("SHAPE_KEY", "Shape Key", ""),
        )
    )

    target_bone: bpy.props.EnumProperty(items=get_bones_enum, name='Bone', default=None)
    target_shape_key: bpy.props.EnumProperty(items=get_shape_key_enum)


class OBJECT_PGT_CGT_RemapDistance(bpy.types.PropertyGroup):
    """ TODO: Remap distance has to be checked for face drivers in the future. """
    # Driver Target
    target: bpy.props.PointerProperty(
        type=bpy.types.Object,
        poll=is_armature,
        description="Select an armature for animation transfer.",
    )

    target_type: bpy.props.EnumProperty(
        name="Target",
        items=(
            ("NONE", "None", ""),
            ("BONE_LEN", "Bone Length", ""),
            ("BONE_DIST", "Bone Distance", ""),
        )
    )
    target_bone: bpy.props.EnumProperty(items=get_bones_enum, name="Bone", default=None)
    target_bone_type: bpy.props.EnumProperty(
        name="Bone Type",
        items=(
            ("HEAD", "Head", ""),
            ("TAIL", "Tail", ""),
            ("LOCATION", "Location", ""),
        )
    )
    other_bone: bpy.props.EnumProperty(items=get_bones_enum, name="Bone", default=None)
    other_bone_type: bpy.props.EnumProperty(
        name="Bone Type",
        items=(
            ("HEAD", "Head", ""),
            ("TAIL", "Tail", ""),
            ("LOCATION", "Location", ""),
        )
    )


class OBJECT_PGT_CGT_ValueMapping(bpy.types.PropertyGroup):
    """ Default value remapping. """
    active: bpy.props.BoolProperty(name="active", default=False)

    remap_none: bpy.props.EnumProperty(
        items=(
            ('DEFAULT', 'DEFAULT', ''),
        ),
        name="Remap Axis")

    remap_default: bpy.props.EnumProperty(
        items=(
            ('DEFAULT', 'DEFAULT', ''),
            ('XYZ', 'XYZ', ""),
            ('XZY', 'XZY', ""),
            ('YXZ', 'YXZ', ""),
            ('YZX', 'YZX', ""),
            ('ZXY', 'ZXY', ""),
            ('ZYX', 'ZYX', "")

        ),
        name="Remap Axis")

    remap_details: bpy.props.EnumProperty(
        items=(
            ('DEFAULT', 'DEFAULT', ''),
            ('X', 'X', ""),
            ('Y', 'Y', ""),
            ('Z', 'Z', ""),
        ),
        name="Remap Axis")

    factor: bpy.props.FloatProperty(name="multiply", default=1.0)
    offset: bpy.props.FloatProperty(name="offset", default=0.0)

    from_min: bpy.props.FloatProperty(name="factor", default=0.0)
    from_max: bpy.props.FloatProperty(name="offset", default=1.0)

    to_min: bpy.props.FloatProperty(name="factor", default=0.0)
    to_max: bpy.props.FloatProperty(name="offset", default=1.0)
# endregion


class OBJECT_PGT_CGT_TransferProperties(bpy.types.PropertyGroup):
    """ Custom remapping properties for objects"""
    active: bpy.props.BoolProperty(default=False)
    driver_type: bpy.props.EnumProperty(
        name="driver_type",
        items=(
            ("NONE", "None", ""),
            ("REMAP", "Remap Value", ""),
            ("CHAIN", "IK Chain", ""),
            ("REMAP_DIST", "Value by Distance", ""),
        )
    )

    # Mapping props
    use_loc_x: bpy.props.PointerProperty(type=OBJECT_PGT_CGT_ValueMapping)
    use_loc_y: bpy.props.PointerProperty(type=OBJECT_PGT_CGT_ValueMapping)
    use_loc_z: bpy.props.PointerProperty(type=OBJECT_PGT_CGT_ValueMapping)
    loc_details: bpy.props.BoolProperty(default=False)

    use_rot_x: bpy.props.PointerProperty(type=OBJECT_PGT_CGT_ValueMapping)
    use_rot_y: bpy.props.PointerProperty(type=OBJECT_PGT_CGT_ValueMapping)
    use_rot_z: bpy.props.PointerProperty(type=OBJECT_PGT_CGT_ValueMapping)
    rot_details: bpy.props.BoolProperty(default=False)

    use_sca_x: bpy.props.PointerProperty(type=OBJECT_PGT_CGT_ValueMapping)
    use_sca_y: bpy.props.PointerProperty(type=OBJECT_PGT_CGT_ValueMapping)
    use_sca_z: bpy.props.PointerProperty(type=OBJECT_PGT_CGT_ValueMapping)
    sca_details: bpy.props.BoolProperty(default=False)

    # Mapping Target
    target: bpy.props.PointerProperty(type=OBJECT_PGT_CGT_TransferTarget)

    # Remapping Objs
    by_obj: bpy.props.PointerProperty(type=OBJECT_PGT_CGT_RemapDistance)

    # for parenting etc
    to_obj: bpy.props.PointerProperty(type=bpy.types.Object)
    from_obj: bpy.props.PointerProperty(type=bpy.types.Object)

    # props relevant for remap by dist
    remap_from_obj: bpy.props.PointerProperty(type=bpy.types.Object)
    remap_to_obj: bpy.props.PointerProperty(type=bpy.types.Object)


classes = [
    OBJECT_PGT_CGT_TransferTarget,
    OBJECT_PGT_CGT_RemapDistance,
    OBJECT_PGT_CGT_ValueMapping,
    OBJECT_PGT_CGT_TransferProperties,
]


def register():
    for cls in classes:
        bpy.utils.register_class(cls)

    bpy.types.Object.cgt_props = bpy.props.PointerProperty(type=OBJECT_PGT_CGT_TransferProperties)


def unregister():
    for cls in reversed(classes):
        bpy.utils.unregister_class(cls)

    del bpy.types.Object.cgt_props
