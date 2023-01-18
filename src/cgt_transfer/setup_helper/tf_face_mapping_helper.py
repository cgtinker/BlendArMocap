import bpy
from collections import namedtuple


# name of target rig
RIGNAME = 'rig'

################################################################
###################### TARGET-BONES ############################
################################################################

# the target is the bone which targets the driver using a constraint
# the remap prop is the bone length which gets used for remapping
BoneTargets = namedtuple('BoneTargets', ['target', 'remap'])

remap_objects = {
    'head':           "head",
    'chin':           "jaw_master",

    'mouth_corner.L': BoneTargets('lips.L', 'DEF-nose.004'),
    'mouth_corner.R': BoneTargets('lips.R', 'DEF-nose.004'),
}

remap_by_distance_objects = {
    # eyes
    'lid.T.L':       BoneTargets('lid.T.L.002', 'DEF-lid.T.L'),
    'lid.B.L':       BoneTargets('lid.B.L.002', 'DEF-lid.T.L'),
    'lid.T.R':       BoneTargets('lid.T.R.002', 'DEF-lid.T.R'),
    'lid.B.R':       BoneTargets('lid.B.R.002', 'DEF-lid.T.R'),

    # eyebrows
    'eyebrow_in.L':  BoneTargets('brow.T.L.003', 'DEF-forehead.L'),
    'eyebrow_mid.L': None,
    'eyebrow_out.L': BoneTargets('brow.T.L.001', 'DEF-forehead.L.002'),
    'eyebrow_in.R':  BoneTargets('brow.T.R.003', 'DEF-forehead.R'),
    'eyebrow_mid.R': None,
    'eyebrow_out.R': BoneTargets('brow.T.R.001', 'DEF-forehead.R.002'),

    # cheeks
    'cheek.L':       BoneTargets('cheek.B.L.001', 'DEF-cheek.T.L.001'),
    'cheek.R':       BoneTargets('cheek.B.R.001', 'DEF-cheek.T.R.001'),

    # mouth
    'lip.T':         BoneTargets('lip.T', 'DEF-nose.004'),
    'lip.B':         BoneTargets('lip.B', 'DEF-chin.001'),
    'lip.L':         BoneTargets('lips.L', 'DEF-lip.T.L.001'),
    'lip.R':         BoneTargets('lips.R', 'DEF-lip.T.R.001'),
}

###############################################################
###################### CONSTRAINTS ############################
###############################################################

# helper dict containing constraints
# which may be used multiple times
default_constraints = {
    "copy_location_offset": {
        'COPY_LOCATION': {
            'owner_space': 'WORLD',
            'use_offset':  True,
            'influence':   1,
        }
    },
}

# dict of constraints which get applied to objects
constraint_dict = {
    "head":           {
        'COPY_ROTATION': {
            'owner_space': 'WORLD',
            'mix_mode':    'ADD',
            'euler_order': 'XYZ',
            'influence':   1,
        },
    },

    "chin":           {
        'COPY_ROTATION': {
            'owner_space': 'LOCAL',
            'mix_mode':    'ADD',
            'euler_order': 'XYZ',
            'influence':   1,
        },
    },

    # eyelids
    'lid.T.L':        default_constraints['copy_location_offset'],
    'lid.B.L':        default_constraints['copy_location_offset'],
    'lid.T.R':        default_constraints['copy_location_offset'],
    'lid.B.R':        default_constraints['copy_location_offset'],

    # eyebrows
    'eyebrow_in.L':   default_constraints['copy_location_offset'],
    'eyebrow_mid.L':  default_constraints['copy_location_offset'],
    'eyebrow_out.L':  default_constraints['copy_location_offset'],
    'eyebrow_in.R':   default_constraints['copy_location_offset'],
    'eyebrow_mid.R':  default_constraints['copy_location_offset'],
    'eyebrow_out.R':  default_constraints['copy_location_offset'],

    # cheeks
    'cheek.L':        default_constraints['copy_location_offset'],
    'cheek.R':        default_constraints['copy_location_offset'],

    # mouth
    'lip.T':          default_constraints['copy_location_offset'],
    'lip.B':          default_constraints['copy_location_offset'],
    'lip.L':          default_constraints['copy_location_offset'],
    'lip.R':          default_constraints['copy_location_offset'],

    'mouth_corner.L': default_constraints['copy_location_offset'],
    'mouth_corner.R': default_constraints['copy_location_offset'],
}

###################################################################
####################### REMAPPING PROPS ###########################
###################################################################

# helper dict containing remapping default properties
remap_defaults = {
    "copy_location": {
        'use_loc_x': {
            'active': True, 'from_min': 0, 'from_max': 1,
            'to_min': 0, 'to_max': 1, 'offset': 0, 'factor': 1},
        'use_loc_y': {
            'active': True, 'from_min': 0, 'from_max': 1,
            'to_min': 0, 'to_max': 1, 'offset': 0, 'factor': 1},
        'use_loc_z': {
            'active': True, 'from_min': 0, 'from_max': 1,
            'to_min': 0, 'to_max': 1, 'offset': 0, 'factor': 1},
    },

    "copy_rotation": {
        'use_rot_x': {
            'active': True, 'from_min': 0, 'from_max': 1,
            'to_min': 0, 'to_max': 1, 'offset': 0, 'factor': 1},
        'use_rot_y': {
            'active': True, 'from_min': 0, 'from_max': 1,
            'to_min': 0, 'to_max': 1, 'offset': 0, 'factor': 1},
        'use_rot_z': {
            'active': True, 'from_min': 0, 'from_max': 1,
            'to_min': 0, 'to_max': 1, 'offset': 0, 'factor': 1},
    },

    "copy_scale":    {
        'use_sca_x': {
            'active': True, 'from_min': 0, 'from_max': 1,
            'to_min': 0, 'to_max': 1, 'offset': 0, 'factor': 1},
        'use_sca_y': {
            'active': True, 'from_min': 0, 'from_max': 1,
            'to_min': 0, 'to_max': 1, 'offset': 0, 'factor': 1},
        'use_sca_z': {
            'active': True, 'from_min': 0, 'from_max': 1,
            'to_min': 0, 'to_max': 1, 'offset': 0, 'factor': 1},
    },
}

# dict of remap properties which gets applied to objects
remap_dict = {
    'head':           remap_defaults['copy_rotation'],
    'chin':           remap_defaults['copy_rotation'],

    'lid.T.L':        {
        'from_obj':       'cgt_face_vertex_145',
        'to_obj':         'cgt_face_vertex_159',
        'remap_from_obj': 'cgt_face_vertex_362',
        'remap_to_obj':   'cgt_face_vertex_263',
        'use_loc_x':      {
            'active':   False,
            'from_min': 0,
            'from_max': 1,
            'to_min':   0,
            'to_max':   1,
            'offset':   -.5,
            'factor':   1,
        },
        'use_loc_z':      {
            'active': True,
        },
    },
    'lid.B.L':        {
        'from_obj':       'cgt_face_vertex_145',
        'to_obj':         'cgt_face_vertex_159',
        'remap_from_obj': 'cgt_face_vertex_362',
        'remap_to_obj':   'cgt_face_vertex_263',
        'use_loc_x':      {
            'active':   False,
            'from_min': 0,
            'from_max': 1,
            'to_min':   0,
            'to_max':   1,
            'offset':   .5,
            'factor':   -1,
        },
        'use_loc_z':      {
            'active': True,
        },
    },
    'lid.T.R':        {
        'from_obj':       'cgt_face_vertex_386',
        'to_obj':         'cgt_face_vertex_374',
        'remap_from_obj': 'cgt_face_vertex_362',
        'remap_to_obj':   'cgt_face_vertex_263',
        'use_loc_x':      {
            'active':   False,
            'from_min': 0,
            'from_max': 1,
            'to_min':   0,
            'to_max':   1,
            'offset':   -.5,
            'factor':   1,
        },
        'use_loc_z':      {
            'active': True,
        },
    },
    'lid.B.R':        {
        'from_obj':       'cgt_face_vertex_386',
        'to_obj':         'cgt_face_vertex_374',
        'remap_from_obj': 'cgt_face_vertex_362',
        'remap_to_obj':   'cgt_face_vertex_263',
        'use_loc_x':      {
            'active':   False,
            'from_min': 0,
            'from_max': 1,
            'to_min':   0,
            'to_max':   1,
            'offset':   .5,
            'factor':   -1
        },
        'use_loc_z':      {
            'active': True,
        },
    },
    'eyebrow_in.L':   {
        'from_obj':       'cgt_face_vertex_55',
        'to_obj':         'cgt_face_vertex_109',
        'remap_from_obj': 'cgt_face_vertex_1',
        'remap_to_obj':   'cgt_face_vertex_6',
        'use_loc_x':      {
            'active':   False,
            'from_min': 0,
            'from_max': 1,
            'to_min':   0,
            'to_max':   1,
            'offset':   -.5,
            'factor':   .5,
        },
        'use_loc_z':      {
            'active': True,
        },
    },
    'eyebrow_mid.L':  {
        'from_obj':       'cgt_face_vertex_223',
        'to_obj':         'cgt_face_vertex_103',
        'remap_from_obj': 'cgt_face_vertex_1',
        'remap_to_obj':   'cgt_face_vertex_6',
        'use_loc_x':      {
            'active':   False,
            'from_min': 0,
            'from_max': 1,
            'to_min':   0,
            'to_max':   1,
            'offset':   -.5,
            'factor':   .5,
        },
        'use_loc_z':      {
            'active': True,
        },
    },
    'eyebrow_out.L':  {
        'from_obj':       'cgt_face_vertex_224',
        'to_obj':         'cgt_face_vertex_54',
        'remap_from_obj': 'cgt_face_vertex_1',
        'remap_to_obj':   'cgt_face_vertex_6',
        'use_loc_x':      {
            'active':   True,
            'from_min': 0,
            'from_max': 1,
            'to_min':   0,
            'to_max':   1,
            'offset':   -.5,
            'factor':   .5,
        },
        'use_loc_z':      {
            'active': True,
        },
    },
    'eyebrow_in.R':   {
        'from_obj':       'cgt_face_vertex_285',
        'to_obj':         'cgt_face_vertex_338',
        'remap_from_obj': 'cgt_face_vertex_1',
        'remap_to_obj':   'cgt_face_vertex_6',
        'use_loc_x':      {
            'active':   False,
            'from_min': 0,
            'from_max': 1,
            'to_min':   0,
            'to_max':   1,
            'offset':   -.5,
            'factor':   .5,
        },
        'use_loc_z':      {
            'active': True,
        },
    },
    'eyebrow_mid.R':  {
        'from_obj':       'cgt_face_vertex_443',
        'to_obj':         'cgt_face_vertex_332',
        'remap_from_obj': 'cgt_face_vertex_1',
        'remap_to_obj':   'cgt_face_vertex_6',
        'use_loc_x':      {
            'active':   False,
            'from_min': 0,
            'from_max': 1,
            'to_min':   0,
            'to_max':   1,
            'offset':   -.5,
            'factor':   .5,
        },
        'use_loc_z':      {
            'active': True,
        },
    },
    'eyebrow_out.R':  {
        'from_obj':       'cgt_face_vertex_444',
        'to_obj':         'cgt_face_vertex_284',
        'remap_from_obj': 'cgt_face_vertex_1',
        'remap_to_obj':   'cgt_face_vertex_6',
        'use_loc_x':      {
            'active':   False,
            'from_min': 0,
            'from_max': 1,
            'to_min':   0,
            'to_max':   1,
            'offset':   -.5,
            'factor':   .5,
        },
        'use_loc_z':      {
            'active': True,
        },
    },
    'cheek.L':        {
        'from_obj':       'cgt_face_vertex_117',
        'to_obj':         'cgt_face_vertex_187',
        'remap_from_obj': 'cgt_face_vertex_1',
        'remap_to_obj':   'cgt_face_vertex_6',
        'use_loc_x':      {
            'active':   False,
            'from_min': 0,
            'from_max': 1,
            'to_min':   0,
            'to_max':   1,
            'offset':   -.5,
            'factor':   .5,
        },
        'use_loc_z':      {
            'active': True,
        },
    },
    'cheek.R':        {
        'from_obj':       'cgt_face_vertex_411',
        'to_obj':         'cgt_face_vertex_348',
        'remap_from_obj': 'cgt_face_vertex_1',
        'remap_to_obj':   'cgt_face_vertex_6',
        'use_loc_x':      {
            'active':   False,
            'from_min': 0,
            'from_max': 1,
            'to_min':   0,
            'to_max':   1,
            'offset':   -.5,
            'factor':   .5,
        },
        'use_loc_z':      {
            'active': True,
        },
    },
    'lip.L':          {
        'from_obj':       'cgt_face_vertex_62',
        'to_obj':         'cgt_face_vertex_292',
        'remap_from_obj': 'cgt_face_vertex_362',
        'remap_to_obj':   'cgt_face_vertex_263',
        'use_loc_x':      {
            'active':   True,
            'from_min': 0,
            'from_max': 1,
            'to_min':   0,
            'to_max':   1,
            'offset':   -.75,
            'factor':   .5,
        },
    },
    'lip.R':          {
        'from_obj':       'cgt_face_vertex_62',
        'to_obj':         'cgt_face_vertex_292',
        'remap_from_obj': 'cgt_face_vertex_362',
        'remap_to_obj':   'cgt_face_vertex_263',
        'use_loc_x':      {
            'active':   True,
            'from_min': 0,
            'from_max': 1,
            'to_min':   0,
            'to_max':   1,
            'offset':   .75,
            'factor':   -.5,
        },
    },
    'lip.T':          {
        'from_obj':       'cgt_face_vertex_13',
        'to_obj':         'cgt_face_vertex_14',
        'remap_from_obj': 'cgt_face_vertex_362',
        'remap_to_obj':   'cgt_face_vertex_263',
        'use_loc_x':      {
            'active':   False,
            'from_min': 0,
            'from_max': 1,
            'to_min':   0,
            'to_max':   1,
            'offset':   0,
            'factor':   .25,
        },
        'use_loc_z':      {
            'active': True,
        },
    },
    'lip.B':          {
        'from_obj':       'cgt_face_vertex_13',
        'to_obj':         'cgt_face_vertex_14',
        'remap_from_obj': 'cgt_face_vertex_362',
        'remap_to_obj':   'cgt_face_vertex_263',
        'use_loc_x':      {
            'active':   False,
            'from_min': 0,
            'from_max': 1,
            'to_min':   0,
            'to_max':   1,
            'offset':   0,
            'factor':   -.25,
        },
        'use_loc_z':      {
            'active': True,
        },
    },
    'mouth_corner.L': {
        'use_loc_x': {
            'active':   False,
            'from_min': 0,
            'from_max': .3,
            'to_min':   -1,
            'to_max':   1,
            'offset':   0,
            'factor':   -.5,
        },
        'use_loc_z': {
            'active': True,
        },
    },
    'mouth_corner.R': {
        'use_loc_x': {
            'active':   False,
            'from_min': 0,
            'from_max': .3,
            'to_min':   -1,
            'to_max':   1,
            'offset':   0,
            'factor':   -.5,
        },
        'use_loc_z': {
            'active': True,
        },
    },
}

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


def get_obj(obj_name: str, col_name: str = 'cgt_DRIVERS'):
    obj = bpy.data.objects.get(obj_name, None)
    if obj is None:
        obj = bpy.data.objects.new(obj_name, None)
        bpy.context.scene.collection.objects.link(obj)
        obj['cgt_id'] = "11b1fb41-1349-4465-b3aa-78db80e8c761"

        for col in obj.users_collection:
            if col.name == col_name:
                continue
            col.objects.unlink(obj)
            collection = bpy.data.collections.get(col_name)
            collection.objects.link(obj)
    return obj


def set_target(obj: bpy.types.Object, rig: bpy.types.Object, target_bone: str):
    """ Set cgt_props target. """
    obj.cgt_props.target.obj_type = 'ARMATURE'
    obj.cgt_props.target.target = rig
    obj.cgt_props.target.armature_type = 'BONE'
    obj.cgt_props.target.target_bone = target_bone


def recv_props(data_path, d, arm=None):
    """ Recursivly apply properites based on dict entries. """
    if data_path is None:
        return

    for k, v in d.items():
        if isinstance(v, dict):
            recv_props(getattr(data_path, k, None), v)
        else:
            if k in ['from_obj', 'to_obj', 'remap_from_obj', 'remap_to_obj']:
                v = get_obj(v)
            setattr(data_path, k, v)


def set_remap_objects_by_distance(rig):
    for obj_name, bone_targets in remap_by_distance_objects.items():
        print(obj_name, bone_targets)
        if bone_targets is None:
            continue

        obj = get_obj(obj_name, 'cgt_FACE')
        set_idle_props(obj.cgt_props)
        set_target(obj, rig, bone_targets.target)

        if obj_name not in remap_dict:
            continue

        obj.cgt_props.by_obj.target = rig
        obj.cgt_props.by_obj.target_type = 'BONE_LEN'
        obj.cgt_props.by_obj.target_bone = bone_targets.remap
        obj.cgt_props.driver_type = 'REMAP_DIST'

        # add constraint
        obj.constraints.clear()
        if obj_name in constraint_dict:
            for key, value in constraint_dict[obj_name].items():
                c = obj.constraints.new(key)
                recv_props(c, value)

        recv_props(obj.cgt_props, remap_dict[obj_name])


def set_remap_objects(rig):
    def remap_object_with_dist(obj_name, target):
        # clean plate obj
        obj = get_obj(obj_name, 'cgt_FACE')
        set_idle_props(obj.cgt_props)
        obj.constraints.clear()
        # targets
        set_target(obj, rig, target.target)
        obj.cgt_props.by_obj.target = rig
        obj.cgt_props.by_obj.target_type = 'BONE_LEN'
        obj.cgt_props.by_obj.target_bone = target.remap
        obj.cgt_props.driver_type = 'REMAP_DIST'

        # add remap props
        obj.cgt_props.driver_type = 'REMAP'
        if obj_name in remap_dict:
            recv_props(obj.cgt_props, remap_dict[obj_name])

        # add constraint
        if obj_name in constraint_dict:
            for key, value in constraint_dict[obj_name].items():
                c = obj.constraints.new(key)
                recv_props(c, value)

    def remap_object_with_none(obj_name, target):
        # clean plate obj
        obj = get_obj(obj_name, 'cgt_FACE')
        set_idle_props(obj.cgt_props)
        obj.constraints.clear()

        # set target and remap type
        set_target(obj, rig, target)
        obj.cgt_props.driver_type = 'REMAP'

        # add constraint
        if obj_name in constraint_dict:
            for key, value in constraint_dict[obj_name].items():
                c = obj.constraints.new(key)
                recv_props(c, value)

        # add remap props
        if obj_name in remap_dict:
            recv_props(obj.cgt_props, remap_dict[obj_name])

    for obj_name, target in remap_objects.items():
        if isinstance(target, str):
            remap_object_with_none(obj_name, target)
        elif isinstance(target, BoneTargets):
            remap_object_with_dist(obj_name, target)


def main():
    rig = bpy.data.objects.get(RIGNAME, None)
    if rig is None:
        objs = bpy.context.selected_objects
        assert len(objs) > 0
        assert objs[0].type == 'ARMATURE'
        rig = objs[0]
    assert rig is not None
    set_remap_objects_by_distance(rig)
    set_remap_objects(rig)


if __name__ == '__main__':
    main()
