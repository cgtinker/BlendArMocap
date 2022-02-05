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
    offset: list = [.0, .0, .0]
    expressions: list = None

    def __init__(self, name):
        self.name = name

    @staticmethod
    def get_detected_joint_length_expression(driver_target):
        return [
            driver_target, "location", "length",
            ["scale.z", "scale.z", "scale.z"],
            ["", "", ""]
        ]

    @staticmethod
    def get_detected_parent_pos_expression(driver_target):
        return [
            driver_target, "location", "prev_pos",
            ["location.x", "location.y", "location.z"],
            ["", "", ""]
        ]

    @staticmethod
    def get_driver_origin_expression(driver_target):
        return [
            driver_target, "location", "origin",
            ["location.x", "location.y", "location.z"],
            ["", "", ""]
        ]

    def get_driver_main_expression(self, driver_target):
        return [
            driver_target, "location", "loc",
            ["location.x", "location.y", "location.z"],
            [f"({self.offset[0]}+origin))+{self.length}/(length)*(-(prev_pos)+",
             f"({self.offset[1]}+origin))+{self.length}/(length)*(-(prev_pos)+",
             f"({self.offset[2]}+origin))+{self.length}/(length)*(-(prev_pos)+"]
        ]


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

    pose_driver_targets = [
        m_CONST.POSE.left_forearm_ik.value, m_CONST.POSE.left_hand_ik.value, m_CONST.POSE.left_index_ik.value,
        m_CONST.POSE.right_forearm_ik.value, m_CONST.POSE.right_hand_ik.value, m_CONST.POSE.right_index_ik.value
    ]

    driven_pose_bone_joints = [
        ["upper_arm_fk.R", "forearm_fk.R"], ["forearm_fk.R", "hand_fk.R"], ["hand_fk.R", "f_middle.01_master.R"],
        ["upper_arm_fk.L", "forearm_fk.L"], ["forearm_fk.L", "hand_fk.L"], ["hand_fk.L", "f_middle.01_master.L"],
    ]

    detected_parent_pos_drivers = [PoseDriver(name) for name in [
        m_CONST.POSE.left_shoulder.value, m_CONST.POSE.left_elbow.value, m_CONST.POSE.left_wrist.value,
        m_CONST.POSE.right_shoulder.value, m_CONST.POSE.right_elbow.value, m_CONST.POSE.right_wrist.value
    ]]

    origin_pose_drivers = [PoseDriver(name) for name in [
        m_CONST.POSE.left_shoulder.value, m_CONST.POSE.left_forearm_ik.value, m_CONST.POSE.left_hand_ik.value,
        m_CONST.POSE.right_shoulder.value, m_CONST.POSE.right_forearm_ik.value, m_CONST.POSE.right_hand_ik.value,
    ]]

    main_pose_drivers = [PoseDriver(name) for name in [
        m_CONST.POSE.left_elbow.value, m_CONST.POSE.left_wrist.value, m_CONST.POSE.left_index.value,
        m_CONST.POSE.right_elbow.value, m_CONST.POSE.right_wrist.value, m_CONST.POSE.right_index.value
    ]]

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
        self.apply_drivers()

    # region mapping
    def set_relation_dict(self, driver_objects: list):
        """ Sets a list of relations for further data transfer. """
        driver_names = [obj.name for obj in driver_objects]
        # pose driver objects
        self.add_pose_driver_mapping(driver_names, driver_objects)
        self.add_constraint_mapping(driver_names, driver_objects)

    def add_pose_driver_mapping(self, driver_names, driver_objects):
        def setup_relation(pose_driver):
            if pose_driver.name in driver_names:
                # access the driver object which has been set up previously
                driver_obj = self.get_driver_object(pose_driver.name, driver_names, driver_objects)
                driver_type = pose_driver.driver_type
                # add pose driver expressions to mapping list
                for expression in pose_driver.expressions:
                    relation = MappingRelation(driver_obj, driver_type, expression)
                    self.mapping_relation_list.append(relation)

        for driver in self.origin_pose_drivers + self.detected_parent_pos_drivers + self.main_pose_drivers:
            setup_relation(driver)

    def add_constraint_mapping(self, driver_names, driver_objects):
        for name in self.pose_constraints:
            if name in driver_names:
                # add constraint to mapping list
                driver_obj = self.get_driver_object(name, driver_names, driver_objects)
                driver_type = DriverType.constraint
                relation = MappingRelation(driver_obj, driver_type, self.pose_constraints[name])
                self.mapping_relation_list.append(relation)

    @staticmethod
    def get_driver_object(driver_name, driver_names, driver_objects):
        idx = driver_names.index(driver_name)
        return driver_objects[idx]

    # endregion

    # region apply drivers
    def apply_drivers(self):
        pose_bone_names = [bone.name for bone in self.pose_bones]

        def apply_by_type(values):
            if driver.driver_type == DriverType.limb_driver:
                target = objects.get_object_by_name(values[0])
                add_driver_batch = self.method_mapping[driver.driver_type]
                add_driver_batch(target, driver.source, values[1], values[2], values[3], values[4])

            elif driver.driver_type == DriverType.constraint:
                if values[0] in pose_bone_names:
                    idx = pose_bone_names.index(values[0])
                    pose_bone = self.pose_bones[idx]

                    add_constraint = self.method_mapping[driver.driver_type]
                    add_constraint(pose_bone, driver.source, values[1])

        for driver in self.mapping_relation_list:
            apply_by_type(driver.values[0])
    # endregion

    # region driver setup
    def set_pose_driver_expressions(self):
        """ sets expressions for drivers """
        # previous ik driver as origin in the chain
        for idx, driver in enumerate(self.origin_pose_drivers):
            print(driver.name)
            origin_expression = driver.get_driver_origin_expression(self.pose_driver_targets[idx])
            driver.expressions = [origin_expression]
            print(origin_expression)

        for idx, driver in enumerate(self.detected_parent_pos_drivers):
            chain_parent = driver.get_detected_parent_pos_expression(self.pose_driver_targets[idx])
            driver.expressions = [chain_parent]

        for idx, driver in enumerate(self.main_pose_drivers):
            scale_expression = driver.get_detected_joint_length_expression(self.pose_driver_targets[idx])
            main_expression = driver.get_driver_main_expression(self.pose_driver_targets[idx])
            driver.expressions = [scale_expression, main_expression]

    def set_pose_driver_joint_length(self):
        """ length of individual arm joints """
        arm_bones = self.get_joints(self.driven_pose_bone_joints, self.pose_bones)
        for idx, joint in enumerate(arm_bones):
            self.main_pose_drivers[idx].length = m_V.get_vector_distance(joint[0], joint[1])

    def set_pose_driver_offset(self):
        """ offset for individual arm joints """
        def set_offset(idx, origin):
            self.main_pose_drivers[idx].offset = self.get_location_offset(
                self.pose_bones,
                self.driven_pose_bone_joints[idx][0],
                origin,
            )
        set_offset(0, m_CONST.POSE.left_shoulder.value)
        set_offset(3, m_CONST.POSE.right_shoulder.value)
    # endregion
