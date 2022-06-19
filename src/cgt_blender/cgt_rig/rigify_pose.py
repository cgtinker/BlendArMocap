'''
Copyright (C) cgtinker, cgtinker.com, hello@cgtinker.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import numpy as np

from . import abs_rigging, limb_drivers
from ..utils import objects
from ...cgt_naming import POSE
from ...cgt_utils import m_V
from .rigify_naming import rigify_pose_bone_names


class RigifyPose(abs_rigging.BpyRigging):
    """ Used for mapping values to drivers, holds rigify bone names and custom data names.
        Objects are getting searched by name, then drivers and constraints get applied. """

    # center of rigify bones
    bone_name_provider = rigify_pose_bone_names.RigifyBoneNameProvider()
    bone_name_provider.update()
    rigify_joints = [
        # arms
        [bone_name_provider.shoulder_c, bone_name_provider.upper_arm_R],
        [bone_name_provider.upper_arm_R, bone_name_provider.forearm_R],
        [bone_name_provider.forearm_R, bone_name_provider.hand_R],
        [bone_name_provider.hand_R, bone_name_provider.finger_R],
        [bone_name_provider.shoulder_c, bone_name_provider.upper_arm_L],
        [bone_name_provider.upper_arm_L, bone_name_provider.forearm_L],
        [bone_name_provider.forearm_L, bone_name_provider.hand_L],
        [bone_name_provider.hand_L, bone_name_provider.finger_L],

        # legs
        [bone_name_provider.hip_c, bone_name_provider.upper_leg_R],
        [bone_name_provider.upper_leg_R, bone_name_provider.knee_R],
        [bone_name_provider.knee_R, bone_name_provider.foot_R],
        [bone_name_provider.foot_R, bone_name_provider.toe_R],
        [bone_name_provider.hip_c, bone_name_provider.upper_leg_L],
        [bone_name_provider.upper_leg_L, bone_name_provider.knee_L],
        [bone_name_provider.knee_L, bone_name_provider.foot_L],
        [bone_name_provider.foot_L, bone_name_provider.toe_L],
    ]

    rigify_bone_center = [
        [bone_name_provider.upper_arm_R, bone_name_provider.upper_arm_L],
        [bone_name_provider.upper_leg_R, bone_name_provider.upper_leg_L]
    ]

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

    # center of ik drivers
    center_driver_targets = [
        POSE.shoulder_center_ik,
        POSE.hip_center_ik
    ]
    # endregion

    def __init__(self, armature, driver_objects: list):
        super().__init__(armature)
        self.pose_constraints = {
            # plain copy rotation
            POSE.hip_center:            [self.bone_name_provider.hip_center, "COPY_ROTATION"],
            POSE.shoulder_center:       [self.bone_name_provider.shoulder_center, "COPY_ROTATION"],

            # arm poses
            POSE.left_hand_ik:          [self.bone_name_provider.hand_ik_R, "CHILD_OF", armature],
            POSE.right_hand_ik:         [self.bone_name_provider.hand_ik_L, "CHILD_OF", armature],
            POSE.left_forearm_ik:       [self.bone_name_provider.forearm_ik_R, "LIMIT_DISTANCE"],
            POSE.right_forearm_ik:      [self.bone_name_provider.forearm_ik_L, "LIMIT_DISTANCE"],

            # damped track to pose driver
            POSE.left_index_ik:         [self.bone_name_provider.hand_ik_R, "LOCKED_TRACK", "TRACK_Y"],
            POSE.right_index_ik:        [self.bone_name_provider.hand_ik_L, "LOCKED_TRACK", "TRACK_Y"],

            # leg poses
            POSE.left_shin_ik:          [self.bone_name_provider.shin_ik_R, "LIMIT_DISTANCE"],
            POSE.right_shin_ik:         [self.bone_name_provider.shin_ik_R, "LIMIT_DISTANCE"],
            POSE.left_foot_ik:          [self.bone_name_provider.foot_ik_R, "CHILD_OF", armature],
            POSE.right_foot_ik:         [self.bone_name_provider.foot_ik_L, "CHILD_OF", armature],
            POSE.left_foot_index_ik:    [self.bone_name_provider.foot_ik_R, "LOCKED_TRACK", "TRACK_NEGATIVE_Y"],
            POSE.right_foot_index_ik:   [self.bone_name_provider.foot_ik_L, "LOCKED_TRACK", "TRACK_NEGATIVE_Y"]
        }

        # reset if overwrite
        bone_names = [pair[0] for key, pair in self.pose_constraints.items()]
        self.remove_bone_constraints(bone_names)

        # region bone center driver setup
        # bone center drivers for limb driver chain
        objects.set_mode('EDIT')
        self.center_points = [m_V.center_point(self.edit_bone_head(v[0]), self.edit_bone_head(v[1]))
                              for v in self.rigify_bone_center]
        objects.set_mode('OBJECT')
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
        self.activate_rigify_poles(user)

        # apply drivers
        self.apply_driver(self.bone_center_drivers)
        self.apply_driver(self.limb_drivers)

        # check if leg transfer
        pose_constraints_copy = self.pose_constraints.copy()
        if not user.experimental_feature_bool:
            remove_list = [POSE.left_shin_ik, POSE.right_shin_ik,
                           POSE.left_foot_ik, POSE.right_foot_ik,
                           POSE.left_foot_index_ik, POSE.right_foot_index_ik]
            for c in remove_list:
                pose_constraints_copy.pop(c, None)

        # apply constraints
        self.apply_constraints(pose_constraints_copy)

    def activate_rigify_poles(self, user):
        """ activate rigify ik poles """
        self.armature.pose.bones[self.bone_name_provider.elbow_pole_L][self.bone_name_provider.pole_key] = 1
        self.armature.pose.bones[self.bone_name_provider.elbow_pole_R][self.bone_name_provider.pole_key] = 1
        if user.experimental_feature_bool:
            self.armature.pose.bones[self.bone_name_provider.knee_pole_R][self.bone_name_provider.pole_key] = 1
            self.armature.pose.bones[self.bone_name_provider.knee_pole_L][self.bone_name_provider.pole_key] = 1

    def get_rigify_joint_lengths(self):
        """ return the lengths of given joints while it uses
            center as keyword for a custom joint origin based on the first index """
        objects.set_mode('EDIT')

        joint_lengths = []
        for joint in self.rigify_joints:
            if self.bone_name_provider.shoulder_c in joint:
                joint_locs = [self.center_points[0], self.edit_bone_head(joint[1])]
            elif self.bone_name_provider.hip_c in joint:
                joint_locs = [self.center_points[1], self.edit_bone_head(joint[1])]
            else:
                joint_locs = [self.edit_bone_head(name) for name in joint]
            length = m_V.get_vector_distance(np.array(joint_locs[0]), np.array(joint_locs[1]))
            joint_lengths.append(length)

        objects.set_mode('OBJECT')
        return joint_lengths
