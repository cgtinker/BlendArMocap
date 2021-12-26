from abc import ABC


def copy_rotation(constraint, target):
    constraint.target = target
    constraint.euler_order = 'XYZ'
    constraint.influence = 1
    constraint.mix_mode = 'ADD'
    constraint.owner_space = 'LOCAL'


class BpyRigging(ABC):
    constraint_mapping = {
        "CAMERA_SOLVER": 0,
        "FOLLOW_TRACK": 1,
        "OBJECT_SOLVER": 2,
        "COPY_LOCATION": 3,
        "COPY_ROTATION": copy_rotation,
        "COPY_SCALE": 5,
        "COPY_TRANSFORMS": 6,
        "LIMIT_DISTANCE": 7,
        "LIMIT_LOCATION": 8,
        "LIMIT_ROTATION": 9,
        "LIMIT_SCALE": 10,
        "MAINTAIN_VOLUME": 11,
        "TRANSFORM": 12,
        "TRANSFORM_CACHE": 13,
        "CLAMP_TO": 14,
        "DAMPED_TRACK": 15,
        "IK": 16,
        "LOCKED_TRACK": 17,
        "SPLINE_IK": 18,
        "STRETCH_TO": 19,
        "TRACK_TO": 20,
        "ACTION": 21,
        "ARMATURE": 22,
        "CHILD_OF": 23,
        "FLOOR": 24,
        "FOLLOW_PATH": 25,
        "PIVOT": 26,
        "SHRINKWRAP": 27
    }

    def add_constraint(self, bone, target, constraint):
        constraints = [c for c in bone.constraints]

        for c in constraints:
            bone.constraints.remove(c)  # Remove constraint

        m_constraint = bone.constraints.new(
            type=constraint
        )
        self.constraint_mapping[constraint](m_constraint, target)


