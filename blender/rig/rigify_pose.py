from blender import objects, abs_rigging
import importlib

importlib.reload(objects)
importlib.reload(abs_rigging)


class RigPose(abs_rigging.BpyRigging):
    # cd pose empty name:       [pose_bone.name,        constraint,         influence]
    def __init__(self, armature, driver_objects):
        self.relation_dict = {}
        self.extension = ""
        self.references = {
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
            "cgt_left_shoulder": ["upper_arm_fk.L", "COPY_ROTATION", None],
            "cgt_right_shoulder": ["upper_arm_fk.R", "COPY_ROTATION", None],
            "cgt_left_elbow": ["forearm_fk.L", "COPY_ROTATION", None],
            "cgt_right_elbow": ["forearm_fk.R", "COPY_ROTATION", None],
            "cgt_left_wrist": [None, None, None],
            "cgt_right_wrist": [None, None, None],
            "cgt_left_pinky": [None, None, None],
            "cgt_right_pinky": [None, None, None],
            "cgt_left_index": [None, None, None],
            "cgt_right_index": [None, None, None],
            "cgt_left_thumb": [None, None, None],
            "cgt_right_thumb": [None, None, None],
            "cgt_left_hip": ["thigh_fk.L", "COPY_ROTATION", None],
            "cgt_right_hip": ["thigh_fk.R", "COPY_ROTATION", None],
            "cgt_left_knee": ["shin_fk.L", "COPY_ROTATION", None],
            "cgt_right_knee": ["shin_fk.R", "COPY_ROTATION", None],
            "cgt_left_ankle": [None, None, None],
            "cgt_right_ankle": [None, None, None],
            "cgt_left_heel": [None, None, None],
            "cgt_right_heel": [None, None, None],
            "cgt_left_foot_index": [None, None, None],
            "cgt_right_foot_index": [None, None, None],

            "hip_center": ["hips", "COPY_ROTATION", None],
            "shoulder_center": ["chest", "COPY_ROTATION", None]
        }
        self.set_relation_dict(driver_objects)
        self.apply_drivers(armature)

    def set_relation_dict(self, driver_empties):
        """ sets relation dict containing bone name and reference empty obj. """
        for empty in driver_empties:
            try:
                bone_name = self.references[empty.name][0]
                if bone_name != None:
                    self.relation_dict[bone_name] = empty

            except KeyError:
                print("driver empty does not exist:", empty.name)

    def apply_drivers(self, armature):
        pose_bones = armature.pose.bones
        for key, value in self.relation_dict.items():
            self.add_constraint(pose_bones[key], value, 'COPY_ROTATION')
