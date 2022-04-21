from abc import ABC

import numpy as np

from .utils import constraints
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
        self.armature = armature
        self.pose_bones = armature.pose.bones

    # region apply
    def n_apply_constraints(self, constraint_dict):
        for key, pair in constraint_dict.items():
            provider = objects.get_object_by_name(key)
            bone = self.pose_bones[pair[0]]
            constraint_name = pair[1]
            args = pair[2:]
            constraints.add_constraint(bone, provider, constraint_name, args)

    def n_apply_driver(self, containers):
        driver_type_dict = {
            driver_interface.DriverType.SINGLE:     driver_types.SinglePropDriver,
            driver_interface.DriverType.BONE:       driver_types.BonePropDriver
        }

        driver_props = [driver for container in containers for driver in container.pose_drivers]
        for prop in driver_props:
            # find objs for drivers
            objs = []
            for p in [[prop.provider_obj, prop.provider_type],
                      [prop.target_object, prop.target_type],
                      [prop.target_rig, None]]:

                ob = None
                if p[1] == driver_interface.ObjectType.OBJECT:
                    ob = objects.get_object_by_name(p[0])
                elif p[1] == driver_interface.ObjectType.BONE:
                    ob = self.pose_bones[p[0]]
                elif p[1] is None and p[0] is not None:
                    ob = self.armature

                objs.append(ob)

            # assign objects
            prop.provider_obj = objs[0]
            prop.target_object = objs[1]
            prop.target_rig = objs[2]

            driver = driver_type_dict[prop.driver_type]
            driver(prop)

    # endregion
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
