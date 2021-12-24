from abc import ABC, abstractmethod


class BpyRigging(ABC):

    @abstractmethod
    def get_reference_bone(self, index):
        """ get a bone by diver index """
        pass

    @staticmethod
    def add_constraint(bone, target):
        constraints = {
            0: "CAMERA_SOLVER",
            1: "FOLLOW_TRACK",
            2: "OBJECT_SOLVER",
            3: "COPY_LOCATION",
            4: "COPY_ROTATION",
            5: "COPY_SCALE",
            6: "COPY_TRANSFORMS",
            7: "LIMIT_DISTANCE",
            8: "LIMIT_LOCATION",
            9: "LIMIT_ROTATION",
            10: "LIMIT_SCALE",
            11: "MAINTAIN_VOLUME",
            12: "TRANSFORM",
            13: "TRANSFORM_CACHE",
            14: "CLAMP_TO",
            15: "DAMPED_TRACK",
            16: "IK",
            17: "LOCKED_TRACK",
            18: "SPLINE_IK",
            19: "STRETCH_TO",
            20: "TRACK_TO",
            21: "ACTION",
            22: "ARMATURE",
            23: "CHILD_OF",
            24: "FLOOR",
            25: "FOLLOW_PATH",
            26: "PIVOT",
            27: "SHRINKWRAP"
        }

        constraint = bone.constraints.new(
            type=constraints[8]
        )

        constraint.target = target
        constraint.influence = 1


