from blender.rig import abstract_rig
from utils import m_V


class RigPose(abstract_rig.Rig):
    # cd pose empty name:       [pose_bone.name,        constraint,         influence]
    mapping = {
        "nose":                 [None,                  None,               None],
        "left_eye_inner":       [None,                  None,               None],
        "left_eye":             [None,                  None,               None],
        "left_eye_outer":       [None,                  None,               None],
        "right_eye_inner":      [None,                  None,               None],
        "right_eye":            [None,                  None,               None],
        "right_eye_outer":      [None,                  None,               None],
        "left_ear":             [None,                  None,               None],
        "right_ear":            [None,                  None,               None],
        "mouth_left":           [None,                  None,               None],
        "mouth_right":          [None,                  None,               None],
        "left_shoulder":        [None,                  20,                 None],  # chest -> track to constraint
        "right_shoulder":       [None,                  20,                 None],  # chest
        "left_elbow":           ["forearm_tweak.L",     3,                  None],
        "right_elbow":          ["forearm_tweak.R",     3,                  None],
        "left_wrist":           ["hand_ik.L",           3,                  None],
        "right_wrist":          ["hand_ik.R",           3,                  None],
        "left_pinky":           [None,                  None,               None],
        "right_pinky":          [None,                  None,               None],
        "left_index":           [None,                  None,               None],
        "right_index":          [None,                  None,               None],
        "left_thumb":           [None,                  None,               None],
        "right_thumb":          [None,                  None,               None],
        "left_hip":             [None,                  4,                  None],   # hips (center point) or torso -> req rotation const
        "right_hip":            [None,                  4,                  None],   # hips (center point) -> also should be rotation between
        "left_knee":            [None,                  None,               None],
        "right_knee":           [None,                  None,               None],
        "left_ankle":           [None,                  None,               None],
        "right_ankle":          [None,                  None,               None],
        "left_heel":            ["foot_ik.L",           3,                  None],
        "right_heel":           ["foot_ik.R",           3,                  None],
        "left_foot_index":      [None,                  None,               None],
        "right_foot_index":     [None,                  None,               None],
    }

    armature = None

    def align_rig(self):
        low_p, high_p = self.get_alignment_points()
        pass

    def get_alignment_points(self):
        r_low = self.get_bone(self.mapping["right_heel"])
        l_low = self.get_bone(self.mapping["left_heel"])
        low_p = m_V.center_point(r_low, l_low)

        r_high = self.get_bone(self.mapping["right_shoulder"])
        l_high = self.get_bone(self.mapping["left_shoulder"])
        high_p = m_V.center_point(r_low, l_low)
        return low_p, high_p

    def get_bone(self, name):
        bone = ""
        return bone

