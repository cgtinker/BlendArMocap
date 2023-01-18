import bpy
from collections import namedtuple


RIG_NAME = 'rig'
USE_IK = True
USE_FK = False

# constrained objects target a bone using a constraint
ConstrainedObject = namedtuple('ConstrainedObject', ['target_bone', 'constraint'])


# default constraint may be used by constrained objects and chain elements
default_constraints = {
    'DEFAULT_COPY_LOCATION':    {
        'COPY_LOCATION': {}
    },

    'DEFAULT_COPY_ROTATION':    {
        'COPY_ROTATION': {}
    },

    'LOCAL_COPY_LOC_AND_ROT':   {
        'COPY_LOCATION': {},
        'COPY_ROTATION': {
            'target_space': 'LOCAL'
        }
    },

    'DEFAULT_COPY_LOC_AND_ROT': {
        'COPY_LOCATION': {},
        'COPY_ROTATION': {}
    }
}

#################################################################
###################### DEFAULT-Setup ############################
#################################################################

constrained_objects = {
    "cgt_hip_center":      ConstrainedObject(
        target_bone="torso",
        constraint=default_constraints['DEFAULT_COPY_ROTATION']),

    "cgt_shoulder_center": ConstrainedObject(
        target_bone="chest",
        constraint=default_constraints['DEFAULT_COPY_ROTATION']),
}

##################################################################
############################ FK-Setup ############################
##################################################################

fk_chains = {
    # ARMS
    "cgt_left_shoulder":  ConstrainedObject(
        target_bone="upper_arm_fk.R",
        constraint=default_constraints['DEFAULT_COPY_ROTATION']),

    "cgt_right_shoulder": ConstrainedObject(
        target_bone="upper_arm_fk.L",
        constraint=default_constraints['DEFAULT_COPY_ROTATION']),

    "cgt_left_elbow":     ConstrainedObject(
        target_bone="forearm_fk.R",
        constraint=default_constraints['DEFAULT_COPY_ROTATION']),

    "cgt_right_elbow":    ConstrainedObject(
        target_bone="forearm_fk.L",
        constraint=default_constraints['DEFAULT_COPY_ROTATION']),

    "cgt_right_wrist":    ConstrainedObject(
        target_bone="hand_fk.R",
        constraint=default_constraints['DEFAULT_COPY_ROTATION']),

    "cgt_left_wrist":     ConstrainedObject(
        target_bone="hand_fk.L",
        constraint=default_constraints['DEFAULT_COPY_ROTATION']),

    # LEGS
    "cgt_left_hip":       ConstrainedObject(
        target_bone="thigh_fk.R",
        constraint=default_constraints['DEFAULT_COPY_ROTATION']),

    "cgt_right_hip":      ConstrainedObject(
        target_bone="thigh_fk.L",
        constraint=default_constraints['DEFAULT_COPY_ROTATION']),

    "cgt_right_knee":     ConstrainedObject(
        target_bone="shin_fk.L",
        constraint=default_constraints['DEFAULT_COPY_ROTATION']),

    "cgt_left_knee":      ConstrainedObject(
        target_bone="shin_fk.R",
        constraint=default_constraints['DEFAULT_COPY_ROTATION']),

    "cgt_right_ankle":    ConstrainedObject(
        target_bone="foot_fk.L",
        constraint=default_constraints['DEFAULT_COPY_ROTATION']),

    "cgt_left_ankle":     ConstrainedObject(
        target_bone="foot_fk.R",
        constraint=default_constraints['DEFAULT_COPY_ROTATION']),
}

##################################################################
############################ IK-Setup ############################
##################################################################

# remap bone to keep constant dist, target bone as mapping target
ChainElement = namedtuple('ChainElement', ['obj', 'parent', 'target_bone', 'remap_bone', 'constraint'])


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
        constraint={}
    )

    elbow = ChainElement(
        obj=suffix + 'elbow',
        parent=shoulder,
        target_bone='forearm_tweak' + prefix,
        remap_bone='upper_arm_fk' + prefix,
        constraint={},
    )

    wrist = ChainElement(
        obj=suffix + 'wrist',
        parent=elbow,
        target_bone='hand_ik' + prefix,
        remap_bone='forearm_fk' + prefix,
        constraint=default_constraints['DEFAULT_COPY_LOC_AND_ROT'],
    )
    return wrist


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
        constraint={},
    )

    knee = ChainElement(
        obj=suffix + 'knee',
        parent=hip,
        target_bone='shin_tweak' + prefix,
        remap_bone='thigh_fk' + prefix,
        constraint={},
    )

    ankle = ChainElement(
        obj=suffix + 'ankle',
        parent=knee,
        target_bone='foot_ik' + prefix,
        remap_bone='shin_fk' + prefix,
        constraint=default_constraints['LOCAL_COPY_LOC_AND_ROT'],
    )
    return ankle


##################################################################
############################ TRANSFER ############################
##################################################################

def set_idle_props(props):
    """ Set CGT_Object_Properties to Idle State. """

    def value_mapping(values):
        values.active = False
        for val in ['factor', 'from_max', 'to_max']:
            setattr(values, val, 1.0)
        for val in ['offset', 'from_min', 'to_min']:
            setattr(values, val, 0.0)

    props.active = False
    props.driver_type = 'NONE'
    for details in ['loc_details', 'rot_details', 'sca_details']:
        setattr(props, details, False)
    for target in ['to_obj', 'from_obj', 'remap_from_obj', 'remap_to_obj']:
        setattr(props, target, None)

    for transform in ['rot', 'loc', 'sca']:
        paths = [f"use_{transform}_{axis}" for axis in ['x', 'y', 'z']]
        for path in paths:
            values = getattr(props, path, None)
            if values is None:
                continue
            value_mapping(values)

    props.target.target = None
    props.by_obj.target = None


def recv_props(data_path, d, arm=None):
    """ Recursivly apply properites based on dict entries. """
    if data_path is None:
        return

    for k, v in d.items():
        if isinstance(v, dict):
            recv_props(getattr(data_path, k, None), v)
        else:
            print(data_path, k, v)
            setattr(data_path, k, v)


def set_remapping_objects(obj_name, constrained_obj, rig, rest=True):
    """ apply default remapping objects. """
    obj = bpy.data.objects.get(obj_name, None)
    assert obj is not None

    if rest:
        set_idle_props(obj.cgt_props)
        obj.constraints.clear()

    # target props
    obj.cgt_props.target.obj_type = 'ARMATURE'
    obj.cgt_props.target.target = rig
    obj.cgt_props.target.armature_type = 'BONE'
    obj.cgt_props.target.target_bone = constrained_obj.target_bone

    # driver type
    obj.cgt_props.driver_type = 'REMAP'
    obj.cgt_props.use_rot_x.active = True
    obj.cgt_props.use_rot_y.active = True
    obj.cgt_props.use_rot_z.active = True

    for constraint_name, props in constrained_obj.constraint.items():
        constraint = obj.constraints.new(constraint_name)
        recv_props(constraint, props)


def set_limb_chain(chain, rig, reset=True):
    """ apply ik limb chains. """
    obj = bpy.data.objects.get(chain.obj, None)
    assert obj is not None

    # reset constraint and obj props
    if reset:
        obj.constraints.clear()
        set_idle_props(obj.cgt_props)

    # target props
    obj.cgt_props.target.obj_type = 'ARMATURE'
    obj.cgt_props.target.target = rig
    obj.cgt_props.target.armature_type = 'BONE'
    obj.cgt_props.target.target_bone = chain.target_bone

    # constraint props
    for constraint_name, props in chain.constraint.items():
        constraint = obj.constraints.new(constraint_name)
        recv_props(constraint, props)

    # chain driver properties
    obj.cgt_props.driver_type = 'CHAIN'
    if chain.parent is None:
        return

    parent = bpy.data.objects.get(chain.parent.obj, None)
    obj.cgt_props.to_obj = parent
    obj.cgt_props.by_obj.target = rig
    obj.cgt_props.by_obj.target_type = 'BONE_LEN'
    obj.cgt_props.by_obj.target_bone = chain.remap_bone

    # traverse
    set_limb_chain(chain.parent, rig, reset)


def main():
    rig = bpy.data.objects.get(RIG_NAME, None)
    if rig is None:
        objs = bpy.context.selected_objects
        assert len(objs) > 0
        assert objs[0].type == 'ARMATURE'
        rig = objs[0]

    assert rig is not None

    # default objects
    for obj_name, constrained_obj in constrained_objects.items():
        set_remapping_objects(obj_name, constrained_obj, rig, True)

    # fk chains
    if USE_FK:
        for obj_name, constrained_obj in fk_chains.items():
            set_remapping_objects(obj_name, constrained_obj, rig, True)

    # ik chains
    if USE_IK:
        reset = not USE_FK and USE_IK
        set_limb_chain(get_arm_chain('.L'), rig, reset)
        set_limb_chain(get_arm_chain('.R'), rig, reset)
        set_limb_chain(get_leg_chain('.L'), rig, reset)
        set_limb_chain(get_leg_chain('.R'), rig, reset)


if __name__ == '__main__':
    main()
