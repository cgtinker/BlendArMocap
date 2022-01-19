from blender import abs_rigging


class RigPose(abs_rigging.BpyRigging):
    def __init__(self, armature, driver_objects: list):
        self.relation_mapping_lst = []
        self.method_mapping = {
        }

        self.references = {
            "face_rotation": "",
            "mouth_driver": "",
            "left_eye_driver": "",
            "right_eye_driver": ""
        }

    def to_do(self):
        """
        1. get distance between mouth up / mouth down
        2. avg dist as location?

        """