from abc import ABC
from dataclasses import dataclass

from .utils import constraints
from .utils.drivers import assignment, driver_types
from ..utils import objects
from ...cgt_utils import m_V


class BpyRigging(ABC):
    @staticmethod
    def add_constraint(bone, target, constraint):
        constraints.add_constraint(bone, target, constraint)

    @staticmethod
    def add_single_prop_driver(driver):
        driver_types.SinglePropDriver(driver)

    @staticmethod
    def add_bone_prop_driver(driver):
        driver_types.BonePropDriver(driver)

    # def add_driver_batch(self, driver_target, driver_source, prop_source, prop_target,
    #                      data_path, func=None, target_rig=None):
    #     """ Add driver to object on x-y-z axis. """
    #     # check if custom prop has been added to the driver
    #     added = self.set_custom_property(driver_target, prop_target, True)

    #     if added is True:
    #         if func is None:
    #             func = ['', '', '']
    #         # attempt to add driver to all axis
    #         for i in range(3):
    #             assignment.add_driver(driver_target, driver_source, prop_source, prop_target,
    #                                   data_path[i], i, func[i], target_rig)
    #     else:
    #         print("Driver may not be applied to same target twice", driver_target.name)

    # # endregion

    # # region custom properties
    # def set_custom_property(self, target_obj, prop_name, prop):
    #     if self.get_custom_property(target_obj, prop_name) == None:
    #         target_obj[prop_name] = prop
    #         return True
    #     else:
    #         return False

    # @staticmethod
    # def get_custom_property(target_obj, prop_name):
    #     try:
    #         value = target_obj[prop_name]
    #     except KeyError:
    #         value = None

    #     return value

    # endregion

    # region way to many lengths
    @staticmethod
    def get_location_offset(pose_bones, bone_name, target):
        # remove constraint before calc offset
        for constraint in pose_bones[bone_name].constraints:
            if constraint.type == "COPY_LOCATION":
                pose_bones[bone_name].constraints.remove(constraint)

        # calc offset
        bone_pos = pose_bones[bone_name].head
        ob = objects.get_object_by_name(target)
        tar = ob.location
        offset = bone_pos - tar

        return offset

    @staticmethod
    def get_average_length(joint_array):
        distances = []
        for joint in joint_array:
            dist = m_V.get_vector_distance(joint[0], joint[1])
            distances.append(dist)
        avg_dist = sum(distances) / len(distances)
        return avg_dist

    def get_average_joint_bone_length(self, joint_bone_names, pose_bones):
        """ requires an array of joints names [[bone_a, bone_b], []... ] and pose bones.
            returns the average length of the connected bones. """
        joints = self.get_joints(joint_bone_names, pose_bones)
        avg_dist = self.get_average_length(joints)
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


# @dataclass(frozen=True)
# class DriverType:
#     LIMB: int = 0
#     CONSTRAINT: int = 1
#     face_driver: int = 2
#     SINGLE: int = 3
#     BONE: int = 4
