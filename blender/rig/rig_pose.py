from blender.rig import abstract_rig
from utils import vector_math


class RigPose(abstract_rig.Rig):
    mapping = {
        "nose":                 [None,                  None],
        "left_eye_inner":       [None,                  None],
        "left_eye":             [None,                  None],
        "left_eye_outer":       [None,                  None],
        "right_eye_inner":      [None,                  None],
        "right_eye":            [None,                  None],
        "right_eye_outer":      [None,                  None],
        "left_ear":             [None,                  None],
        "right_ear":            [None,                  None],
        "mouth_left":           [None,                  None],
        "mouth_right":          [None,                  None],
        "left_shoulder":        [None,                  20],  # chest -> track to constraint
        "right_shoulder":       [None,                  20],  # chest
        "left_elbow":           ["forearm_tweak.L",     3],
        "right_elbow":          ["forearm_tweak.R",     3],
        "left_wrist":           ["hand_ik.L",           3],
        "right_wrist":          ["hand_ik.R",           3],
        "left_pinky":           [None,                  None],
        "right_pinky":          [None,                  None],
        "left_index":           [None,                  None],
        "right_index":          [None,                  None],
        "left_thumb":           [None,                  None],
        "right_thumb":          [None,                  None],
        "left_hip":             [None,                  4],   # hips (center point) or torso -> req rotation const
        "right_hip":            [None,                  4],   # hips (center point) -> also should be rotation between
        "left_knee":            [None,                  None],
        "right_knee":           [None,                  None],
        "left_ankle":           [None,                  None],
        "right_ankle":          [None,                  None],
        "left_heel":            ["foot_ik.L",           3],
        "right_heel":           ["foot_ik.R",           3],
        "left_foot_index":      [None,                  None],
        "right_foot_index":     [None,                  None],
    }

    armature = None

    def align_rig(self):
        low_p, high_p = self.get_alignment_points()
        pass

    def get_alignment_points(self):
        r_low = self.get_bone(self.mapping["right_heel"])
        l_low = self.get_bone(self.mapping["left_heel"])
        low_p = vector_math.get_center_point(r_low, l_low)

        r_high = self.get_bone(self.mapping["right_shoulder"])
        l_high = self.get_bone(self.mapping["left_shoulder"])
        high_p = vector_math.get_center_point(r_low, l_low)
        return low_p, high_p

    def get_bone(self, name):
        bone = ""
        return bone

