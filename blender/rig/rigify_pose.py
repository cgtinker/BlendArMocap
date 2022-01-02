from blender.rig import abstract_rig


class RigPose(abstract_rig.Rig):
    # cd pose empty name:       [pose_bone.name,        constraint,         influence]
    mapping = {
        "nose": [None, None, None],
        "left_eye_inner": [None, None, None],
        "left_eye": [None, None, None],
        "left_eye_outer": [None, None, None],
        "right_eye_inner": [None, None, None],
        "right_eye": [None, None, None],
        "right_eye_outer": [None, None, None],
        "left_ear": [None, None, None],
        "right_ear": [None, None, None],
        "mouth_left": [None, None, None],
        "mouth_right": [None, None, None],
        "left_shoulder": ["upper_arm_fk.L", "COPY_ROTATION", None],
        "right_shoulder": ["upper_arm_fk.R", "COPY_ROTATION", None],
        "left_elbow": ["forearm_fk.L", "COPY_ROTATION", None],
        "right_elbow": ["forearm_fk.R", "COPY_ROTATION", None],
        "left_wrist": [None, None, None],
        "right_wrist": [None, None, None],
        "left_pinky": [None, None, None],
        "right_pinky": [None, None, None],
        "left_index": [None, None, None],
        "right_index": [None, None, None],
        "left_thumb": [None, None, None],
        "right_thumb": [None, None, None],
        "left_hip": ["thigh_fk.L", "COPY_ROTATION", None],
        "right_hip": ["thigh_fk.R", "COPY_ROTATION", None],
        "left_knee": ["shin_fk.L", "COPY_ROTATION", None],
        "right_knee": ["shin_fk.R", "COPY_ROTATION", None],
        "left_ankle": [None, None, None],
        "right_ankle": [None, None, None],
        "left_heel": [None, None, None],
        "right_heel": [None, None, None],
        "left_foot_index": [None, None, None],
        "right_foot_index": [None, None, None],

        "hip_center": ["hips", "COPY_ROTATION", None],
        "shoulder_center": ["chest", "COPY_ROTATION", None]
    }

    armature = None
