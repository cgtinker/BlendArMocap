from . import abs_rigging
from .utils.drivers import limb_drivers
from ...cgt_naming import POSE
from ...cgt_utils import m_V


class RigifyPose(abs_rigging.BpyRigging):
    pose_constraints = {
        # plain copy rotation
        POSE.hip_center:       ["torso", "COPY_ROTATION"],
        POSE.shoulder_center:  ["chest", "COPY_ROTATION"],

        # copy pose driver location
        POSE.left_hand_ik:     ["hand_ik.R", "COPY_LOCATION_WORLD"],
        POSE.right_hand_ik:    ["hand_ik.L", "COPY_LOCATION_WORLD"],
        POSE.left_forearm_ik:  ["forearm_tweak.R", "COPY_LOCATION_WORLD"],
        POSE.right_forearm_ik: ["forearm_tweak.L", "COPY_LOCATION_WORLD"],

        # damped track to pose driver
        POSE.left_index_ik:    ["hand_ik.R", "DAMPED_TRACK"],
        POSE.right_index_ik:   ["hand_ik.L", "DAMPED_TRACK"]
    }

    # region bone center drivers
    center_driver_targets = [
        POSE.shoulder_center_ik
    ]

    shoulder_center = ["upper_arm_fk.R", "upper_arm_fk.L"]
    hip_center = ["", ""]
    # endregion

    # region limb drivers
    limb_driver_targets = [
        POSE.left_shoulder_ik, POSE.left_forearm_ik,
        POSE.left_hand_ik, POSE.left_index_ik,

        POSE.right_shoulder_ik, POSE.right_forearm_ik,
        POSE.right_hand_ik, POSE.right_index_ik
    ]

    rigify_joints = [
        ["shoulder_center", "upper_arm_fk.R"], ["upper_arm_fk.R", "forearm_fk.R"],
        ["forearm_fk.R", "hand_fk.R"], ["hand_fk.R", "f_middle.01_master.R"],

        ["shoulder_center", "upper_arm_fk.L"], ["upper_arm_fk.L", "forearm_fk.L"],
        ["forearm_fk.L", "hand_fk.L"], ["hand_fk.L", "f_middle.01_master.L"],
    ]

    ik_driver_origins = [
        POSE.shoulder_center_ik, POSE.left_shoulder_ik,
        POSE.left_forearm_ik, POSE.left_hand_ik,

        POSE.shoulder_center_ik, POSE.right_shoulder_ik,
        POSE.right_forearm_ik, POSE.right_hand_ik,
    ]

    detected_joints = [
        [POSE.shoulder_center, POSE.left_shoulder], [POSE.left_shoulder, POSE.left_elbow],
        [POSE.left_elbow, POSE.left_wrist], [POSE.left_wrist, POSE.left_index],

        [POSE.shoulder_center, POSE.right_shoulder], [POSE.right_shoulder, POSE.right_elbow],
        [POSE.right_elbow, POSE.right_wrist], [POSE.right_wrist, POSE.right_index]
    ]
    # endregion

    def __init__(self, armature, driver_objects: list):
        self.pose_bones = armature.pose.bones

        # region bone center driver setup
        self.m_shoulder_center = m_V.center_point(
            self.bone_head(self.shoulder_center[0]),
            self.bone_head(self.shoulder_center[1]))
        self.hip_center = None
        joint_lengths = self.get_rigify_joint_lengths()

        self.bone_center_drivers = [limb_drivers.BoneCenter(
            driver_target=target,
            bones=self.shoulder_center,
            target_rig=armature
        ) for idx, target in enumerate(self.center_driver_targets)]
        # endregion

        # region limb driver setup
        self.limb_drivers = [limb_drivers.LimbDriver(
            driver_target=target,
            driver_origin=self.ik_driver_origins[idx],
            detected_joint=self.detected_joints[idx],
            rigify_joint_length=joint_lengths[idx],
        ) for idx, target in enumerate(self.limb_driver_targets)]
        # endregion

        self.set_relation_dict(driver_objects)
        self.apply_drivers()

    def get_rigify_joint_lengths(self):
        """ return the lengths of given joints while it uses
            center as keyword for a custom joint origin based on the first index """

        joint_lengths = []
        for joint in self.rigify_joints:
            if "shoulder_center" in joint:
                joint_locs = [self.m_shoulder_center, self.bone_head(joint[1])]
            elif "hip_center" in joint:
                joint_locs = [self.hip_center, self.bone_head(joint[1])]
            else:
                joint_locs = [self.bone_head(name) for name in joint]
            length = m_V.get_vector_distance(joint_locs[0], joint_locs[1])
            joint_lengths.append(length)
        return joint_lengths

    # region mapping relation setup
    def set_relation_dict(self, driver_objects: list):
        """ Sets a list of relations for further data transfer. """
        driver_names = [obj.name for obj in driver_objects]
        self.set_bone_driver_mapping(self.bone_center_drivers)
        self.set_single_prop_driver_mapping(self.limb_drivers, driver_names, driver_objects)
        self.set_constraint_mapping(self.pose_constraints, driver_names, driver_objects)
    # endregion
