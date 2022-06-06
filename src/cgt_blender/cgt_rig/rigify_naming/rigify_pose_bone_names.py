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

from . import bone_name_provider


class RigifyBoneNameProvider(bone_name_provider.BoneNameProvider):
    # ik targets
    shoulder_center = "chest"
    hip_center = "torso"

    hand_ik_R = "hand_ik.R"
    hand_ik_L = "hand_ik.L"
    elbow_pole_R = "upper_arm_parent.R"
    elbow_pole_L = "upper_arm_parent.L"
    forearm_ik_R = "upper_arm_ik_target.R"
    forearm_ik_L = "upper_arm_ik_target.L"
    shin_ik_R = "thigh_ik_target.R"
    shin_ik_L = "thigh_ik_target.L"
    knee_pole_R = "thigh_parent.R"
    knee_pole_L = "thigh_parent.L"
    foot_ik_R = "foot_ik.R"
    foot_ik_L = "foot_ik.L"

    pole_key = "pole_vector"

    # references
    shoulder_c = "shoulder_center"
    upper_arm_R = "upper_arm_fk.R"
    forearm_R = "forearm_fk.R"
    hand_R = "hand_fk.R"
    finger_R = "f_middle.01_master.R"

    upper_arm_L = "upper_arm_fk.L"
    forearm_L = "forearm_fk.L"
    hand_L = "hand_fk.L"
    finger_L = "f_middle.01_master.L"

    hip_c = "hip_center"
    upper_leg_R = "thigh_fk.R"
    knee_R = "shin_fk.R"
    foot_R = "foot_fk.R"
    toe_R = "toe.R"

    upper_leg_L = "thigh_fk.L"
    knee_L = "shin_fk.L"
    foot_L = "foot_fk.L"
    toe_L = "toe.L"

    rigify_bone_center = None
    rigify_joints = None

    def set_rv65_bone_names(self):
        self.toe_L = "toe_fk.L"
        self.toe_R = "toe_fk.R"
