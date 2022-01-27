
def copy_rotation(constraint, target, *args):
    constraint.target = target
    constraint.euler_order = 'XYZ'
    constraint.influence = 1
    constraint.mix_mode = 'ADD'
    constraint.owner_space = 'LOCAL'


def copy_location(constraint, target, *args):
    constraint.target = target
    constraint.influence = 1
    constraint.owner_space = 'POSE'


def copy_location_offset(bone, target, *args):
    constraint = bone.constraints.new(
        type="COPY_LOCATION"
    )
    constraint.target = target
    constraint.influence = 1
    constraint.use_offset = True
    constraint.owner_space = 'POSE'


def damped_track(constraint, target, *args):
    constraint.target = target
    constraint.influence = 1
    constraint.track_axis = 'TRACK_Y'
    constraint.owner_space = 'POSE'