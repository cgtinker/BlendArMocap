from . import abs_reference
from .. import cgt_naming


class CustomPose(abs_reference.BoneNameProvider):
    name = "pose"

    def provide_bone_names(self):
        pass
