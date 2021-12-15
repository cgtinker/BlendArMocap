from utils import log


class RigifyHands():
    def __init__(self):
        # tips naming convention in rigify has some flaws?
        self.references = {
            "WRIST": "hand_fk",
            "THUMB_CMC": "thumb.01",
            "THUMB_MCP": "thumb.02",
            "THUMP_IP": "thumb.03",
            "THUMB_TIP": "thumb.01.L.001",
            "INDEX_FINGER_MCP": "f_index.01",
            "INDEX_FINGER_PIP": "f_index.02",
            "INDEX_FINGER_DIP": "f_index.03",
            "INDEX_FINGER_TIP": "f_index.01",
            "MIDDLE_FINGER_MCP": "f_middle.01",
            "MIDDLE_FINGER_PIP": "f_middle.02",
            "MIDDLE_FINGER_DIP": "f_middle.03",
            "MIDDLE_FINGER_TIP": "f_middle.01",
            "RING_FINGER_MCP": "f_ring.01",
            "RING_FINGER_PIP": "f_ring.02",
            "RING_FINGER_DIP": "f_ring.03",
            "RING_FINGER_TIP": "f_ring.01",
            "PINKY_MCP": "f_pinky.01",
            "PINKY_PIP": "f_pinky.02",
            "PINKY_DIP": "f_pinky.03",
            "PINKY_TIP": "f_pinky.01",
        }

        self.relation_dict = {}
        self.extension = ""

    def get_reference_name(self, key):
        if "TIP" in key:
            ref = self.references[key] + self.extension + ".001"
            return ref

        ref = self.references[key] + self.extension
        return ref

    def get_bones(self):
        pass

    def set_relation_dict(self, hand_empties):
        # left or right hand
        if ".L" in hand_empties[0]:
            self.extension = ".L"
        elif ".R" in hand_empties[0]:
            self.extension = ".R"

        for empty in hand_empties:
            # remove extension
            name = empty.name.replace(self.extension, "")
            try:
                self.relation_dict[self.get_reference_name(name)] = empty
            except KeyError:
                log.logger.Error("Driver empty does not exist: ", empty.name)

    def add_contraints(self, pose_bones):
        for bone in pose_bones:
            add_constraint(bone, "")


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
