from . import objects


def copy_rotation(constraint, target, values):
    constraint.target = target
    constraint.euler_order = 'XYZ'
    constraint.influence = 1
    constraint.mix_mode = 'ADD'
    constraint.owner_space = 'LOCAL'


def limit_rotation(constraint, target, values):
    constraint.use_limit_x = True
    constraint.min_x = values[0][0]
    constraint.max_x = values[0][1]
    constraint.influence = 1
    constraint.owner_space = 'LOCAL'


def copy_rotation_world_space(bone, target, values):
    constraint = bone.constraints.new(
        type="COPY_ROTATION"
    )
    constraint.target = target
    constraint.euler_order = 'XYZ'
    constraint.influence = 1
    constraint.mix_mode = 'ADD'
    constraint.owner_space = 'WORLD'


def copy_location(constraint, target, values):
    constraint.target = target
    constraint.influence = 1
    constraint.owner_space = 'POSE'


def copy_location_offset(bone, target, values):
    constraint = bone.constraints.new(
        type="COPY_LOCATION"
    )
    constraint.target = target
    constraint.influence = 1
    constraint.use_offset = True
    constraint.owner_space = 'WORLD'


def copy_location_world(bone, target, values):
    constraint = bone.constraints.new(
        type="COPY_LOCATION"
    )
    constraint.target = target
    constraint.influence = 1
    constraint.owner_space = 'WORLD'


def copy_location_world_offset(bone, target, values):
    constraint = bone.constraints.new(
        type="COPY_LOCATION"
    )
    objects.set_pose_bone_world_position(bone, values[0], [0, 0, 0])
    constraint.target = target
    constraint.influence = 1
    constraint.use_offset = True
    constraint.owner_space = 'WORLD'


def child_of(constraint, target, values):
    objects.set_pose_bone_world_position(values[1], values[0], target.location)
    constraint.target = target
    constraint.influence = 1
    constraint.set_inverse_pending = True


def damped_track(constraint, target, values):
    constraint.target = target
    constraint.influence = 1
    constraint.owner_space = 'POSE'
    constraint.track_axis = 'TRACK_NEGATIVE_Y'


def track_to(constraint, target, values):
    constraint.target = target
    constraint.influence = 1
    constraint.owner_space = 'LOCAL'
    constraint.up_axis = 'UP_X'
    constraint.track_axis = 'TRACK_Y'


def locked_track(constraint, target, values=None):
    if values is None:
        values = ['TRACK_Y']
    constraint.target = target
    constraint.influence = 1
    constraint.track_axis = values[0]
    constraint.lock_axis = 'LOCK_Z'


def limit_distance(constraint, target, values):
    constraint.target = target
    constraint.distance = 0.05
    constraint.owner_space = 'WORLD'
    constraint.target_space = 'WORLD'


constraint_mapping = {
    "CAMERA_SOLVER":        0,
    "FOLLOW_TRACK":         1,
    "OBJECT_SOLVER":        2,
    "COPY_LOCATION":        copy_location,
    "COPY_LOCATION_OFFSET": copy_location_offset,
    "COPY_LOCATION_WORLD":  copy_location_world,
    "COPY_LOCATION_WORLD_OFFSET": copy_location_world_offset,
    "COPY_ROTATION":        copy_rotation,
    "COPY_ROTATION_WORLD":  copy_rotation_world_space,
    "COPY_SCALE":           5,
    "COPY_TRANSFORMS":      6,
    "LIMIT_DISTANCE":       limit_distance,
    "LIMIT_LOCATION":       8,
    "LIMIT_ROTATION":       limit_rotation,
    "LIMIT_SCALE":          10,
    "MAINTAIN_VOLUME":      11,
    "TRANSFORM":            12,
    "TRANSFORM_CACHE":      13,
    "CLAMP_TO":             14,
    "DAMPED_TRACK":         damped_track,
    "IK":                   16,
    "LOCKED_TRACK":         locked_track,
    "SPLINE_IK":            18,
    "STRETCH_TO":           19,
    "TRACK_TO":             track_to,
    "ACTION":               21,
    "ARMATURE":             22,
    "CHILD_OF":             child_of,
    "FLOOR":                24,
    "FOLLOW_PATH":          25,
    "PIVOT":                26,
    "SHRINKWRAP":           27,
}


def add_constraint(bone, target, constraint, values):
    """ Bit hacky way to apply constraints even of the same type. """
    # TODO: apply proper refactoring
    m_constraints = [c for c in bone.constraints]
    # overwriting constraint by
    # removing previously added constraints if types match
    for c in m_constraints:
        # prepare target constraint
        target_constraint = constraint
        if "_OFFSET" in constraint:
            target_constraint = target_constraint.replace("_OFFSET", "")

        if "_WORLD" in constraint:
            target_constraint = target_constraint.replace("_WORLD", "")

        # match syntax of bpy constraint
        constraint_name = c.name
        constraint_name = constraint_name.replace(" ", "_")
        constraint_name = constraint_name.upper()
        constraint_name = constraint_name.rsplit('.', 1)[0]

        # remove if names match
        if constraint_name == target_constraint:
            bone.constraints.remove(c)
    try:
        # adding a new constraint
        m_constraint = bone.constraints.new(
            type=constraint
        )

        if 'CHILD_OF' in constraint:
            values.append(bone)
        constraint_mapping[constraint](m_constraint, target, values)
    except TypeError or KeyError:
        # call custom method with bone
        constraint_mapping[constraint](bone, target, values)
