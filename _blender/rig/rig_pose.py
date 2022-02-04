import importlib

import m_CONST
from _blender.rig import abs_rigging
from _blender.rig.abs_rigging import DriverType, MappingRelation
from _blender.utils import objects
from utils import m_V

importlib.reload(m_CONST)
importlib.reload(m_V)
importlib.reload(objects)
importlib.reload(abs_rigging)


class PoseDriver:
    target = None
    length: int = .0
    offset: int = .0
    expressions = []

    def __init__(self, target):
        self.target = target

    def driver_scale_attr(self, target):
        attribute = [
            target, "location", "scale",
            ["scale.z", "scale.z", "scale.z"],
            ["", "", ""]]
        self.expressions.append(attribute)

    def driver_expression(self, driver_target, offset, avg_length):
        attribute = [
            driver_target, "location", "location",
            ["location.x", "location.y", "location.z"],
            [f"{offset[0]}+{avg_length}/(scale) *",
             f"{offset[1]}+{avg_length}/(scale) *",
             f"{offset[2]}+{avg_length}/(scale) *"]]
        self.expressions.append(attribute)


class RigPose(abs_rigging.BpyRigging):
    driven_pose_bone_names = [
        # left arm
        ["upper_arm_fk.L", "forearm_fk.L"],
        ["forearm_fk.L", "hand_fk.L"],
        ["hand_fk.L", "f_middle.01_master.L"],
        # right arm
        ["upper_arm_fk.R", "forearm_fk.R"],
        ["forearm_fk.R", "hand_fk.R"],
        ["hand_fk.R", "f_middle.01_master.R"]
    ]

    pose_constraints = {
        # plain copy rotation
        m_CONST.POSE.hip_center.value:  ["torso", "COPY_ROTATION"],
        m_CONST.POSE.shoulder_center.value: ["chest", "COPY_ROTATION"],
        # copy pose driver location
        m_CONST.POSE.left_hand_ik.value: ["hand_ik.R", "COPY_LOCATION"],
        m_CONST.POSE.right_hand_ik.value: ["hand_ik.L", "COPY_LOCATION"],
        m_CONST.POSE.left_forearm_ik.value: ["forearm_tweak.R", "COPY_LOCATION"],
        m_CONST.POSE.right_forearm_ik.value: ["forearm_tweak.L", "COPY_LOCATION"],
        # damped track to pose driver
        m_CONST.POSE.left_index_ik.value: ["hand_ik.R", "DAMPED_TRACK"],
        m_CONST.POSE.right_index_ik.value: ["hand_ik.L", "DAMPED_TRACK"]
    }

    pose_driver_names = [
        m_CONST.POSE.left_elbow.value,
        m_CONST.POSE.left_wrist.value,
        m_CONST.POSE.left_index.value,
        m_CONST.POSE.right_elbow.value,
        m_CONST.POSE.right_wrist.value,
        m_CONST.POSE.right_index.value
    ]

    pose_drivers = [PoseDriver(name) for name in pose_driver_names]

    def __init__(self, armature, driver_objects: list):
        self.pose_bones = armature.pose.bones

        self.method_mapping = {
            DriverType.limb_driver: self.add_driver_batch,
            DriverType.constraint: self.add_constraint
        }

        # offsets and avg data based on rigify rig
        self.set_pose_driver_joint_length()
        self.set_pose_driver_offset()

    def set_pose_driver_joint_length(self):
        """ length of individual arm joints """
        arm_bones = self.get_joints(self.driven_pose_bone_names, self.pose_bones)
        for idx, joint in enumerate(arm_bones):
            self.pose_drivers[idx].length = m_V.get_vector_distance(joint[0], joint[1])

    def set_pose_driver_offset(self):
        """ offset for individual arm joints """
        joint_origins = [
            m_CONST.POSE.left_shoulder.value,
            m_CONST.POSE.left_elbow.value,
            m_CONST.POSE.left_wrist.value,
            m_CONST.POSE.right_shoulder.value,
            m_CONST.POSE.right_elbow.value,
            m_CONST.POSE.right_wrist.value
        ]

        for idx, origin in enumerate(joint_origins):
            self.pose_drivers[idx].offset = self.get_location_offset(
                self.pose_bones,
                self.driven_pose_bone_names[idx][0],
                origin
            )
