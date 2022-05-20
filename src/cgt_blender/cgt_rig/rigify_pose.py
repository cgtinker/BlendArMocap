import numpy as np

from . import abs_rigging
from .drivers import limb_drivers
from ..utils import objects
from ...cgt_naming import POSE
from ...cgt_utils import m_V


class RigifyPose(abs_rigging.BpyRigging):
    """ Used for mapping values to drivers, holds rigify bone names and custom data names.
        Objects are getting searched by name, then drivers and constraints get applied. """

    # center of ik drivers
    center_driver_targets = [
        POSE.shoulder_center_ik,
        POSE.hip_center_ik
    ]

    # center of rigify bones
    rigify_bone_center = [
        ["upper_arm_fk.R", "upper_arm_fk.L"],
        ["thigh_fk.R", "thigh_fk.L"]]

    # region limb drivers
    # driver targets
    limb_driver_targets = [
        # arms
        POSE.left_shoulder_ik, POSE.left_forearm_ik,
        POSE.left_hand_ik, POSE.left_index_ik,
        POSE.right_shoulder_ik, POSE.right_forearm_ik,
        POSE.right_hand_ik, POSE.right_index_ik,
        # legs
        POSE.left_hip_ik, POSE.left_shin_ik,
        POSE.left_foot_ik, POSE.left_foot_index_ik,
        POSE.right_hip_ik, POSE.right_shin_ik,
        POSE.right_foot_ik, POSE.right_foot_index_ik
    ]

    # joints of the rig
    rigify_joints = [
        # arms
        ["shoulder_center", "upper_arm_fk.R"], ["upper_arm_fk.R", "forearm_fk.R"],
        ["forearm_fk.R", "hand_fk.R"], ["hand_fk.R", "f_middle.01_master.R"],
        ["shoulder_center", "upper_arm_fk.L"], ["upper_arm_fk.L", "forearm_fk.L"],
        ["forearm_fk.L", "hand_fk.L"], ["hand_fk.L", "f_middle.01_master.L"],

        # legs
        ["torso", "thigh_fk.R"], ["thigh_fk.R", "shin_fk.R"],
        ["shin_fk.R", "foot_fk.R"], ["foot_fk.R", "toe.R"],
        ["torso", "thigh_fk.L"], ["thigh_fk.L", "shin_fk.L"],
        ["shin_fk.L", "foot_fk.L"], ["foot_fk.L", "toe.L"]
    ]

    # origins of the drivers (getting previous pos of driver)
    ik_driver_origins = [
        # arms
        POSE.shoulder_center_ik, POSE.left_shoulder_ik,
        POSE.left_forearm_ik, POSE.left_hand_ik,
        POSE.shoulder_center_ik, POSE.right_shoulder_ik,
        POSE.right_forearm_ik, POSE.right_hand_ik,

        # legs
        POSE.hip_center_ik, POSE.left_hip_ik,
        POSE.left_shin_ik, POSE.left_foot_ik,
        POSE.hip_center_ik, POSE.right_hip_ik,
        POSE.right_shin_ik, POSE.right_foot_ik
    ]

    detected_joints = [
        # arms
        [POSE.shoulder_center, POSE.left_shoulder], [POSE.left_shoulder, POSE.left_elbow],
        [POSE.left_elbow, POSE.left_wrist], [POSE.left_wrist, POSE.left_index],
        [POSE.shoulder_center, POSE.right_shoulder], [POSE.right_shoulder, POSE.right_elbow],
        [POSE.right_elbow, POSE.right_wrist], [POSE.right_wrist, POSE.right_index],
        # legs
        [POSE.hip_center, POSE.left_hip], [POSE.left_hip, POSE.left_knee],
        [POSE.left_knee, POSE.left_ankle], [POSE.left_ankle, POSE.left_foot_index],
        [POSE.hip_center, POSE.right_hip], [POSE.right_hip, POSE.right_knee],
        [POSE.right_knee, POSE.right_ankle], [POSE.right_ankle, POSE.right_foot_index]
    ]

    # endregion

    def __init__(self, armature, driver_objects: list):
        super().__init__(armature)
        self.pose_constraints = {
            # plain copy rotation
            POSE.hip_center:            ["torso", "COPY_ROTATION"],
            POSE.shoulder_center:       ["chest", "COPY_ROTATION"],

            # arm poses
            POSE.left_hand_ik:          ["hand_ik.R", "CHILD_OF", armature],
            POSE.right_hand_ik:         ["hand_ik.L", "CHILD_OF", armature],
            POSE.left_forearm_ik:       ["upper_arm_ik_target.R", "LIMIT_DISTANCE"],
            POSE.right_forearm_ik:      ["upper_arm_ik_target.L", "LIMIT_DISTANCE"],

            # damped track to pose driver
            POSE.left_index_ik:         ["hand_ik.R", "LOCKED_TRACK", "TRACK_Y"],
            POSE.right_index_ik:        ["hand_ik.L", "LOCKED_TRACK", "TRACK_Y"],

            # leg poses
            POSE.left_shin_ik:          ["thigh_ik_target.R", "LIMIT_DISTANCE"],
            POSE.right_shin_ik:         ["thigh_ik_target.L", "LIMIT_DISTANCE"],
            POSE.left_foot_ik:          ["foot_ik.R", "CHILD_OF", armature],
            POSE.right_foot_ik:         ["foot_ik.L", "CHILD_OF", armature],
            POSE.left_foot_index_ik:    ["foot_ik.R", "LOCKED_TRACK", "TRACK_NEGATIVE_Y"],
            POSE.right_foot_index_ik:   ["foot_ik.L", "LOCKED_TRACK", "TRACK_NEGATIVE_Y"]
        }

        # region bone center driver setup
        # bone center drivers for limb driver chain
        self.center_points = [m_V.center_point(self.bone_head(v[0]), self.bone_head(v[1]))
                              for v in self.rigify_bone_center]
        self.bone_center_drivers = [limb_drivers.BoneCenter(
            driver_target=target,
            bones=self.rigify_bone_center[idx],
            target_rig=armature,
        ) for idx, target in enumerate(self.center_driver_targets)]
        # endregion

        # region limb driver setup
        # limb driver contain the rigify ik target position in world space
        joint_lengths = self.get_rigify_joint_lengths()
        self.limb_drivers = [limb_drivers.LimbDriver(
            driver_target=target,
            driver_origin=self.ik_driver_origins[idx],
            detected_joint=self.detected_joints[idx],
            rigify_joint_length=joint_lengths[idx],
        ) for idx, target in enumerate(self.limb_driver_targets)]

        # activate ik poles
        user = objects.user_pref()
        self.toggle_rigify_poles(user)

        # apply drivers
        self.apply_driver(self.bone_center_drivers)
        self.apply_driver(self.limb_drivers)

        # check if leg transfer
        pose_constraints_copy = self.pose_constraints.copy()
        if not user.experimental_feature_bool:
            remove_list = [POSE.left_shin_ik, POSE.right_shin_ik, POSE.left_foot_ik, POSE.right_foot_ik]
            for c in remove_list:
                pose_constraints_copy.pop(c, None)

        # apply constraints
        self.apply_constraints(pose_constraints_copy)

    def toggle_rigify_poles(self, user):
        """ activate rigify ik poles """
        self.armature.pose.bones["upper_arm_parent.L"]["pole_vector"] = 1
        self.armature.pose.bones["upper_arm_parent.R"]["pole_vector"] = 1
        if user.experimental_feature_bool:
            self.armature.pose.bones["thigh_parent.R"]["pole_vector"] = 1
            self.armature.pose.bones["thigh_parent.L"]["pole_vector"] = 1

    def get_rigify_joint_lengths(self):
        """ return the lengths of given joints while it uses
            center as keyword for a custom joint origin based on the first index """

        joint_lengths = []
        for joint in self.rigify_joints:
            if "shoulder_center" in joint:
                joint_locs = [self.center_points[0], self.bone_head(joint[1])]
            elif "hip_center" in joint:
                joint_locs = [self.center_points[1], self.bone_head(joint[1])]
            else:
                joint_locs = [self.bone_head(name) for name in joint]
            length = m_V.get_vector_distance(np.array(joint_locs[0]), np.array(joint_locs[1]))
            joint_lengths.append(length)
        return joint_lengths
