from . import RigReference
from .. import cgt_naming


class CustomPose(RigReference.BoneNameProvider):
    name = "pose"

    def provide_bone_names(self):
        pass
