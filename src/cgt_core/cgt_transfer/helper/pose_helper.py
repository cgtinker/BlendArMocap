import bpy
from collections import namedtuple

ChainElement = namedtuple('ChainElement', ['obj', 'parent', 'target_bone', 'remap_bone', 'constraint'])
ConstrainedObject = namedtuple('ConstrainedObject', ['target_bone', 'constraint'])

constrained_objects = {
    "cgt_hip_center":      ConstrainedObject("torso", "COPY_ROTATION"),
    "cgt_shoulder_center": ConstrainedObject("chest", "COPY_ROTATION"),
}


# Reconstruct the ik chain in reverserd.
def get_arm_chain(prefix='.L'):
    if prefix == '.L':
        suffix = 'cgt_right_'
    elif prefix == '.R':
        suffix = 'cgt_left_'
    else:
        raise ValueError

    shoulder = ChainElement(
        obj=suffix + 'shoulder',
        parent=None,
        target_bone='upper_arm_fk' + prefix,
        remap_bone='',
        constraint=None
    )

    elbow = ChainElement(
        obj=suffix + 'elbow',
        parent=shoulder,
        target_bone='forearm_tweak' + prefix,
        remap_bone='upper_arm_fk' + prefix,
        constraint='COPY_LOCATION',
    )

    wrist = ChainElement(
        obj=suffix + 'wrist',
        parent=elbow,
        target_bone='hand_ik' + prefix,
        remap_bone='forearm_fk' + prefix,
        constraint='COPY_LOCATION'
    )
    return wrist


# Reconstruct the ik chain in reverserd.
def get_leg_chain(prefix='.L'):
    if prefix == '.L':
        suffix = 'cgt_right_'
    elif prefix == '.R':
        suffix = 'cgt_left_'
    else:
        raise ValueError

    hip = ChainElement(
        obj=suffix + 'hip',
        parent=None,
        target_bone='thigh_fk' + prefix,
        remap_bone='',
        constraint=None,
    )

    knee = ChainElement(
        obj=suffix + 'knee',
        parent=hip,
        target_bone='shin_tweak' + prefix,
        remap_bone='thigh_fk' + prefix,
        constraint='COPY_LOCATION',
    )

    ankle = ChainElement(
        obj=suffix + 'ankle',
        parent=knee,
        target_bone='foot_ik' + prefix,
        remap_bone='shin_fk' + prefix,
        constraint='COPY_LOCATION',
    )
    return ankle


def set_pose_properties(rig):
    def _pass(*args, **kwargs):
        pass

    # define constraint usage
    def copy_loc(ob):
        c = ob.constraints.new(type='COPY_LOCATION')

    def copy_rot(ob):
        c = ob.constraints.new(type='COPY_ROTATION')

    # map to constraint funcs
    constraint_dict = {
        'COPY_LOCATION': copy_loc,
        'COPY_ROTATION': copy_rot,
        None:            _pass
    }

    def set_limb_chain(chain):
        nonlocal rig
        obj = bpy.data.objects.get(chain.obj, None)
        assert obj is not None

        # target props
        obj.cgt_props.target.obj_type = 'ARMATURE'
        obj.cgt_props.target.target = rig
        obj.cgt_props.target.armature_type = 'BONE'
        obj.cgt_props.target.target_bone = chain.target_bone

        # chain driver properties
        obj.cgt_props.driver_type = 'CHAIN'
        obj.constraints.clear()
        constraint_dict[chain.constraint](obj)
        if chain.parent is None:
            return

        parent = bpy.data.objects.get(chain.parent.obj, None)
        obj.cgt_props.to_obj = parent
        obj.cgt_props.by_obj.target = rig
        obj.cgt_props.by_obj.target_type = 'BONE_LEN'
        obj.cgt_props.by_obj.target_bone = chain.remap_bone

        # traverse
        set_limb_chain(chain.parent)

    def set_remapping_objects(obj_name, ref):
        nonlocal rig
        obj = bpy.data.objects.get(obj_name, None)
        assert obj is not None

        # target props
        obj.cgt_props.target.obj_type = 'ARMATURE'
        obj.cgt_props.target.target = rig
        obj.cgt_props.target.armature_type = 'BONE'
        obj.cgt_props.target.target_bone = ref.target_bone

        obj.constraints.clear()
        constraint_dict[ref.constraint](obj)

    set_limb_chain(get_arm_chain('.L'))
    set_limb_chain(get_arm_chain('.R'))
    # set_limb_chain(get_leg_chain('.L'))
    # set_limb_chain(get_leg_chain('.R'))

    for k, v in constrained_objects.items():
        set_remapping_objects(k, v)


def main():
    rig = bpy.data.objects.get('rig', None)
    assert rig is not None
    set_pose_properties(rig)


if __name__ == '__main__':
    main()
