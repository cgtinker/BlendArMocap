from . import bpy_instance_provider
from ..cgt_blender.utils import objects
from ..cgt_naming import POSE, COLLECTIONS


class BpyPoseReferences(bpy_instance_provider.BpyInstanceProvider):
    references = {
        # MEDIAPIPE DEFAULTS
        0:  POSE.nose,
        1:  POSE.left_eye_inner,
        2:  POSE.left_eye,
        3:  POSE.left_eye_outer,
        4:  POSE.right_eye_inner,
        5:  POSE.right_eye,
        6:  POSE.right_eye_outer,
        7:  POSE.left_ear,
        8:  POSE.right_ear,
        9:  POSE.mouth_left,
        10: POSE.mouth_right,
        11: POSE.left_shoulder,
        12: POSE.right_shoulder,
        13: POSE.left_elbow,
        14: POSE.right_elbow,
        15: POSE.left_wrist,
        16: POSE.right_wrist,
        17: POSE.left_pinky,
        18: POSE.right_pinky,
        19: POSE.left_index,
        20: POSE.right_index,
        21: POSE.left_thumb,
        22: POSE.right_thumb,
        23: POSE.left_hip,
        24: POSE.right_hip,
        25: POSE.left_knee,
        26: POSE.right_knee,
        27: POSE.left_ankle,
        28: POSE.right_ankle,
        29: POSE.left_heel,
        30: POSE.right_heel,
        31: POSE.left_foot_index,
        32: POSE.right_foot_index,
    }

    drivers = {
        33: POSE.left_forearm_ik,
        34: POSE.right_forearm_ik,
        35: POSE.left_hand_ik,
        36: POSE.right_hand_ik,
        37: POSE.left_index_ik,
        38: POSE.right_index_ik,

        39: POSE.right_foot_ik,
        40: POSE.left_foot_ik,
        41: POSE.left_shin_ik,
        42: POSE.right_shin_ik,

        43: POSE.left_shoulder_ik,
        44: POSE.right_shoulder_ik,
        45: POSE.left_hip_ik,
        46: POSE.right_hip_ik,
        47: POSE.shoulder_center_ik,
        48: POSE.hip_center_ik,
        49: POSE.left_foot_index_ik,
        50: POSE.right_foot_index_ik
    }

    shoulder_center = bpy_instance_provider.CustomData()
    hip_center = bpy_instance_provider.CustomData()

    pose = []
    col_name = COLLECTIONS.pose

    def __init__(self):
        self.pose = objects.add_empties(self.references, 0.025)
        self.pose += objects.add_empties(self.drivers, 0.025)

        objects.add_list_to_collection(self.col_name, self.pose, self.parent_col)

        self.init_bpy_driver_obj(
            self.shoulder_center, self.pose, 0.01, POSE.shoulder_center, self.col_name, "SPHERE",
            [0, 0, 0])
        self.init_bpy_driver_obj(
            self.hip_center, self.pose, 0.01, POSE.hip_center, self.col_name, "SPHERE", [0, 0, 0])

    def get_instances(self):
        return self.pose, self.shoulder_center, self.hip_center

    def set_position(self, data, frame):
        """Keyframe the position of input data."""
        try:
            self.translate(self.pose, data, frame)

        except IndexError:
            print("VALUE ERROR WHILE ASSIGNING POSE POSITION")

    def set_rotation(self, data, frame):
        """ Apply rotation data. """
        self.euler_rotate(self.pose, data, frame)

    def set_scale(self, data, frame):
        """ Apply scale data. """
        self.scale(self.pose, data, frame)

