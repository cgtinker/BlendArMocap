from abc import ABC, abstractmethod

import numpy as np

from .utils import constraints, mapping
from .utils.drivers import driver_types, driver_interface
from ..utils import objects
from ...cgt_utils import m_V


class BpyRigging(ABC):
    pose_bones: list = None
    mapping_relation_list: list = None
    method_mapping = {
        driver_interface.DriverType.CONSTRAINT: constraints.add_constraint,
        driver_interface.DriverType.SINGLE:     driver_types.SinglePropDriver,
        driver_interface.DriverType.BONE:       driver_types.BonePropDriver
    }

    def __init__(self, armature):
        self.mapping_relation_list = []
        self.pose_bones = armature.pose.bones

    @abstractmethod
    def set_relation_dict(self, driver_objects: list):
        pass

    # region apply drivers
    def apply_drivers(self):
        """ applies all mapping relations for mapping values
            gets target method by driver type."""
        pose_bone_names = [bone.name for bone in self.pose_bones]

        def apply_by_type(mapping_relation):
            # print("Attempt to apply", mapping_relation)
            def constraint():
                if mapping_relation.driver_target in pose_bone_names:

                    # get pose bone
                    idx = pose_bone_names.index(mapping_relation.driver_target)
                    pose_bone = self.pose_bones[idx]

                    # add constraint to bone
                    add_constraint = self.method_mapping[mapping_relation.driver_type]
                    add_constraint(pose_bone,
                                   mapping_relation.driver_source,
                                   mapping_relation.values[0],
                                   mapping_relation.values[1:])

            def driver():
                driver_container = mapping_relation.driver_target

                # if ob already found, pass
                if type(driver_container.target_object) == str:
                    driver_container.target_object = objects.get_object_by_name(driver_container.target_object)

                # assign values as driver
                driver_container.provider_obj = mapping_relation.driver_source
                driver_method = self.method_mapping[driver_container.driver_type]
                driver_method(driver_container)

            # type determines target method
            relations = {
                driver_interface.DriverType.CONSTRAINT: constraint,
                driver_interface.DriverType.BONE:       driver,
                driver_interface.DriverType.SINGLE:     driver,
            }

            relations[mapping_relation.driver_type]()

        # apply all mapping relation based on their types
        for m_mapping_relation in self.mapping_relation_list:
            apply_by_type(m_mapping_relation)

    # endregion

    # region mapping
    def set_bone_relation(self, driver_containers: list):
        def setup_relation(pose_driver):
            # requires bone names for setup
            pose_bone_names = [bone.name for bone in self.pose_bones]
            if pose_driver.provider_obj in pose_bone_names:
                driver_obj = self.pose_bones[pose_driver.provider_obj]
                # create a mapping relation
                relation = mapping.MappingRelation(driver_obj, pose_driver.driver_type, pose_driver)
                self.mapping_relation_list.append(relation)

        for containers in driver_containers:
            # print("Processing Container", containers)
            for driver in containers.pose_drivers:
                # print("Preparing Driver", driver)
                setup_relation(driver)

    def set_single_prop_relation(self, driver_containers: list, driver_names: list, driver_objects: list):
        def setup_relation(pose_driver):
            # get the provider object by name
            if pose_driver.provider_obj in driver_names:
                driver_obj = self.get_driver_object(pose_driver.provider_obj, driver_names, driver_objects)
                # create a mapping relation
                relation = mapping.MappingRelation(driver_obj, pose_driver.driver_type, pose_driver)
                self.mapping_relation_list.append(relation)

        for containers in driver_containers:
            # print("Processing Container", containers)
            for driver in containers.pose_drivers:
                # print("Preparing Driver", driver)
                setup_relation(driver)

    def set_constraint_relation(self, constraint_dict: dict, driver_names: list, driver_objects: list):
        for name in constraint_dict:
            if name in driver_names:
                # get driver source object and set driver type
                driver_obj = self.get_driver_object(name, driver_names, driver_objects)
                driver_type = driver_interface.DriverType.CONSTRAINT
                # create a mapping relation (source, type, driver, values)
                relation = mapping.MappingRelation(
                    driver_source=driver_obj,
                    driver_type=driver_type,
                    driver_target=constraint_dict[name][0],
                    values=constraint_dict[name][1:])
                # print("Setting constraint", relation)
                self.mapping_relation_list.append(relation)

    # endregion

    @staticmethod
    def get_driver_object(driver_name, driver_names, driver_objects):
        idx = driver_names.index(driver_name)
        return driver_objects[idx]

    def bone_head(self, bone_name):
        return self.pose_bones[bone_name].head

    # region joint length
    def get_average_joint_bone_length(self, joint_bone_names, pose_bones):
        """ requires an array of joints names [[bone_a, bone_b], []... ] and pose bones.
            returns the average length of the connected bones. """
        joints = self.get_joints(joint_bone_names, pose_bones)
        avg_dist = self.get_average_length(joints)
        return avg_dist

    @staticmethod
    def get_average_length(joint_array):
        distances = []
        for joint in joint_array:
            dist = m_V.get_vector_distance(np.array(joint[0]), np.array(joint[1]))
            distances.append(dist)
        avg_dist = sum(distances) / len(distances)
        return avg_dist

    @staticmethod
    def get_joints(joint_names, pose_bones):
        """ requires an array of joints names [[bone_a, bone_b], []... ] and pose bones.
        returns the bone head locations in the same formatting. """
        arm_joints = []
        for names in joint_names:

            joint = []
            for name in names:
                bone_pos = pose_bones[name].head
                joint.append(bone_pos)

            arm_joints.append(joint)
        return arm_joints
    # endregion
