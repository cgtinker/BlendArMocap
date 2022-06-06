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

from abc import ABC

import numpy as np

from ..utils import objects, driver_interface, driver_types, constraints
from ...cgt_utils import m_V


class BpyRigging(ABC):
    pose_bones: list = None
    mapping_relation_list: list = None

    def __init__(self, armature):
        self.mapping_relation_list = []
        self.armature = armature
        self.pose_bones = armature.pose.bones

    # region apply
    def apply_constraints(self, constraint_dict):
        user_prefs = objects.user_pref()
        overwrite = user_prefs.overwrite_drivers_bool  # noqa

        """ Applies constraints to bones targeting objects. """
        for key, pair in constraint_dict.items():
            provider = objects.get_object_by_name(key)
            bone = self.pose_bones[pair[0]]
            constraint_name = pair[1]
            args = pair[2:]
            constraints.add_constraint(bone, provider, constraint_name, args, overwrite)

    def apply_driver(self, containers):
        """ Applies containers of driver properties as drivers to objects.
            The properties are given as strings, the objects are searched by types. """

        # driver types targets
        driver_type_dict = {
            driver_interface.DriverType.SINGLE: driver_types.SinglePropDriver,
            driver_interface.DriverType.BONE:   driver_types.BonePropDriver,
            driver_interface.DriverType.CUSTOM: driver_types.CustomBonePropDriver
        }

        # wrapper for convenience
        def get_pose_bone(bone_name):
            return self.pose_bones[bone_name]

        ref_provider_dict = {
            driver_interface.ObjectType.OBJECT: objects.get_object_by_name,
            driver_interface.ObjectType.BONE:   get_pose_bone,
        }

        # prepare for iteration
        driver_props = [driver for container in containers for driver in container.pose_drivers]

        drivers_types = []
        props = []

        # search references for proper driver setup
        for prop in driver_props:
            # find bone ref or object ref for driver
            prop.provider_obj = ref_provider_dict[prop.provider_type](prop.provider_obj)
            prop.target_object = ref_provider_dict[prop.target_type](prop.target_object)

            # assign custom vars
            if prop.target_rig is not None:
                prop.target_rig = self.armature
            if prop.custom_target_props is not None:
                objects.set_custom_property(prop.provider_obj, prop.custom_target_props.name,
                                            prop.custom_target_props.value, -5, 5, overwrite=True)

            # set driver type for execution
            driver = driver_type_dict[prop.driver_type]

            # append gathered data to lists
            drivers_types.append(driver)
            props.append(prop)

        # check if overwrite by user is enabled
        user_prefs = objects.user_pref()
        overwrite = user_prefs.overwrite_drivers_bool # noqa

        # remove all existing drivers before applying new ones when overwriting
        if overwrite is True:
            for prop in driver_props:
                try:
                    for d in prop.target_object.animation_data.drivers:
                        prop.target_object.animation_data.drivers.remove(d)
                except AttributeError:
                    # drivers may not be applied previously
                    pass

        # execute the drivers
        for i in range(0, len(drivers_types)):
            drivers_types[i](props[i])

    # endregion
    def bone_head(self, bone_name):

        # returns the bone head position of a pose bone
        return self.pose_bones[bone_name].head

    def remove_bone_constraints(self, bones):
        # reset if overwrite
        # remove constraints if overwrite
        user_prefs = objects.user_pref()
        if user_prefs.overwrite_drivers_bool:
            from ..utils import constraints
            import bpy
            for bone_name in bones:
                constraints.remove_constraints(self.pose_bones[bone_name])  # pair 0 = bone name in dict
            bpy.context.view_layer.update()
        # endregion

    # region joint length
    def get_average_joint_bone_length(self, joint_bone_names, pose_bones):
        """ requires an array of joints names [[bone_a, bone_b], []... ] and pose bones.
            returns the average length of the connected bones. """
        joints = self.get_joints(joint_bone_names, pose_bones)
        avg_dist = self.get_average_length(joints)
        return avg_dist

    @staticmethod
    def get_average_length(joint_array):
        """ takes an array of positions [[pos_a, pos_b], ...]
            returns the average length of the input array"""
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
