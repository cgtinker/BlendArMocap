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
    name: str = None
    driver_type: DriverType = DriverType.limb_driver
    length: float = .0
    offset: list = None
    expressions: list = None

    def __init__(self, name):
        self.name = name

    @staticmethod
    def set_driver_scale_expression(driver_target):
        return [
            driver_target, "location", "scale",
            ["scale.z", "scale.z", "scale.z"],
            ["", "", ""]]

    def set_driver_main_expression(self, driver_target):
        return [
            driver_target, "location", "location",
            ["location.x", "location.y", "location.z"],
            [f"{self.offset[0]}+{self.length}/(scale) *",
             f"{self.offset[1]}+{self.length}/(scale) *",
             f"{self.offset[2]}+{self.length}/(scale) *"]]


class RigPose(abs_rigging.BpyRigging):
    pose_constraints = {
        # plain copy rotation
        m_CONST.POSE.hip_center.value: ["torso", "COPY_ROTATION"],
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
        m_CONST.POSE.left_elbow.value, m_CONST.POSE.left_wrist.value, m_CONST.POSE.left_index.value,
        m_CONST.POSE.right_elbow.value, m_CONST.POSE.right_wrist.value, m_CONST.POSE.right_index.value
    ]

    pose_driver_targets = [
        m_CONST.POSE.left_forearm_ik.value, m_CONST.POSE.left_hand_ik.value, m_CONST.POSE.left_index_ik.value,
        m_CONST.POSE.right_forearm_ik.value, m_CONST.POSE.right_hand_ik.value, m_CONST.POSE.right_index_ik.value
    ]

    driven_pose_bone_joints = [
        ["upper_arm_fk.L", "forearm_fk.L"], ["forearm_fk.L", "hand_fk.L"], ["hand_fk.L", "f_middle.01_master.L"],
        ["upper_arm_fk.R", "forearm_fk.R"], ["forearm_fk.R", "hand_fk.R"], ["hand_fk.R", "f_middle.01_master.R"]
    ]

    pose_drivers = [PoseDriver(name) for name in pose_driver_names]
    mapping_relation_list = []

    def __init__(self, armature, driver_objects: list):
        self.pose_bones = armature.pose.bones

        self.method_mapping = {
            DriverType.limb_driver: self.add_driver_batch,
            DriverType.constraint: self.add_constraint
        }

        # pose driver setup based on input rig
        self.set_pose_driver_joint_length()
        self.set_pose_driver_offset()
        self.set_pose_driver_expressions()

        self.set_relation_dict(driver_objects)

    # region mapping
    def set_relation_dict(self, driver_objects: list):
        """ Sets a list of relations for further data transfer. """
        driver_names = [obj.name for obj in driver_objects]
        # pose driver objects
        self.add_pose_driver_mapping(driver_names, driver_objects)
        # self.add_constraint_mapping(driver_names, driver_objects)

    def add_pose_driver_mapping(self, driver_names, driver_objects):
        for pose_driver in self.pose_drivers:
            if pose_driver.name in driver_names:
                print("\n", pose_driver.name)
                driver_obj = self.get_driver_object(pose_driver.name, driver_names, driver_objects)
                driver_type = pose_driver.driver_type

                # add pose driver expressions to mapping list
                for expression in pose_driver.expressions:
                    relation = MappingRelation(driver_obj, driver_type, expression)
                    print(relation)
                    self.mapping_relation_list.append(relation)

    def add_constraint_mapping(self, driver_names, driver_objects):
        for name in self.pose_constraints:
            if name in driver_names:
                print(name)
                # add constraint to mapping list
                driver_obj = self.get_driver_object(name, driver_names, driver_objects)
                driver_type = DriverType.constraint
                relation = MappingRelation(driver_obj, driver_type, self.pose_constraints[name])
                print(relation)
                self.mapping_relation_list.append(relation)

    @staticmethod
    def get_driver_object(driver_name, driver_names, driver_objects):
        idx = driver_names.index(driver_name)
        return driver_objects[idx]
    # endregion

    # region driver setup
    def set_pose_driver_expressions(self):
        """ sets expressions for drivers """
        for idx, driver in enumerate(self.pose_drivers):
            scale_expression = driver.set_driver_scale_expression(driver.name)
            main_expression = driver.set_driver_main_expression(self.pose_driver_targets[idx])
            driver.expressions = [scale_expression, main_expression]

    def set_pose_driver_joint_length(self):
        """ length of individual arm joints """
        arm_bones = self.get_joints(self.driven_pose_bone_joints, self.pose_bones)
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
                self.driven_pose_bone_joints[idx][0],
                origin
            )
    # endregion
