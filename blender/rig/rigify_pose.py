import importlib

from blender import objects, abs_rigging

importlib.reload(objects)
importlib.reload(abs_rigging)

"""
references
            "cgt_nose": [None, None, None],
            "cgt_left_eye_inner": [None, None, None],
            "cgt_left_eye": [None, None, None],
            "cgt_left_eye_outer": [None, None, None],
            "cgt_right_eye_inner": [None, None, None],
            "cgt_right_eye": [None, None, None],
            "cgt_right_eye_outer": [None, None, None],
            "cgt_left_ear": [None, None, None],
            "cgt_right_ear": [None, None, None],
            "cgt_mouth_left": [None, None, None],
            "cgt_mouth_right": [None, None, None],
            "cgt_left_shoulder": [None, None, None],
            "cgt_right_shoulder": [None, None, None],
            "cgt_left_elbow": [None, None, None],
            "cgt_right_elbow": [None, None, None],
            "cgt_left_wrist": [None, None, None],
            "cgt_right_wrist": [None, None, None],
            "cgt_left_pinky": [None, None, None],
            "cgt_right_pinky": [None, None, None],
            "cgt_left_index": [None, None, None],
            "cgt_right_index": [None, None, None],
            "cgt_left_thumb": [None, None, None],
            "cgt_right_thumb": [None, None, None],
            "cgt_left_hip": [None, None, None],
            "cgt_right_hip": [None, None, None],
            "cgt_left_knee": [None, None, None],
            "cgt_right_knee": [None, None, None],
            "cgt_left_ankle": [None, None, None],
            "cgt_right_ankle": [None, None, None],
            "cgt_left_heel": [None, None, None],
            "cgt_right_heel": [None, None, None],
            "cgt_left_foot_index": [None, None, None],
            "cgt_right_foot_index": [None, None, None],

            "hip_center":       [None, None, None],
            "shoulder_center":  [None, None, None]
"""

class RigPose(abs_rigging.BpyRigging):
    # cd pose empty name:       [pose_bone.name,        constraint,         influence]
    def __init__(self, armature, driver_objects):
        self.relation_dict = {}
        self.extension = ""
        self.driver_references = {
            "cgt_left_shoulder": [None, None, None],
            "cgt_right_shoulder": [None, None, None],
            "cgt_left_elbow": [None, None, None],
            "cgt_right_elbow": [None, None, None],
            "cgt_left_wrist": [None, None, None],
            "cgt_right_wrist": [None, None, None],

            "cgt_left_hip": [None, None, None],
            "cgt_right_hip": [None, None, None],
            "cgt_left_knee": [None, None, None],
            "cgt_right_knee": [None, None, None],
            "cgt_left_ankle": [None, None, None],
            "cgt_right_ankle": [None, None, None],
        }
        self.constraint_references = {
            "hip_center": ["hips", "COPY_ROTATION", None],
            "shoulder_center": ["chest", "COPY_ROTATION", None]
        }

        self.set_relation_dict(driver_objects)
        self.apply_drivers(armature)

    def set_relation_dict(self, driver_empties):
        """ sets relation dict containing bone name and reference empty obj. """
        for empty in driver_empties:
            try:
                bone_name = self.constraint_references[empty.name][0]
                if bone_name != None:
                    self.relation_dict[bone_name] = empty

            except KeyError:
                print("driver empty does not exist:", empty.name)

    # todo: just rotation drivers for now, still have to add avg scale drivers
    def apply_drivers(self, armature):
        pose_bones = armature.pose.bones
        for key, value in self.relation_dict.items():
            self.add_constraint(pose_bones[key], value, 'COPY_ROTATION')
