from blender.rig import abs_rigging
from blender.rig.abs_rigging import DriverType, MappingRelation
from blender.utils import objects
from utils import m_V

import importlib
importlib.reload(m_V)
importlib.reload(objects)
importlib.reload(abs_rigging)


class RigifyPose(abs_rigging.BpyRigging):
    arm_bones = [
        # left arm
        ["upper_arm_fk.L", "forearm_fk.L"],
        ["forearm_fk.L", "hand_fk.L"],
        # right arm
        ["upper_arm_fk.R", "forearm_fk.R"],
        ["forearm_fk.R", "hand_fk.R"],
    ]

    leg_bones = [
        # right left
        ["thigh_ik.R", "shin_tweak.R"],
        ["shin_tweak.R", "foot_ik.R"],
        # left leg
        ["thigh_ik.L", "shin_tweak.L"],
        ["shin_tweak.L", "foot_ik.L"]
    ]

    def __init__(self, armature, driver_objects: list):
        self.pose_bones = armature.pose.bones
        # storing relation between rigify rig and driver rig in an array (drivers may be used multiple times)
        self.relation_mapping_lst = []
        self.method_mapping = {
            DriverType.limb_driver: self.add_driver_batch,
            DriverType.constraint: self.add_constraint
        }

        # offsets and avg data based on rigify input rig
        self.avg_arm_length, self.avg_leg_length = self.get_avg_limb_length()
        self.left_arm_offset, self.right_arm_offset, self.left_leg_offset, self.right_leg_offset = self.get_limb_offsets()

        # mapping for drivers with multiple users
        self.multi_user_driver_dict = {
            "cgt_left_shoulder": ["cgt_left_hand_ik_driver", "cgt_left_forearm_ik_driver", "cgt_left_index_ik_driver"],
            "cgt_right_shoulder": ["cgt_right_hand_ik_driver", "cgt_right_forearm_ik_driver", "cgt_right_index_ik_driver"],
            "cgt_left_hip": ["cgt_left_shin_ik_driver", "cgt_left_foot_ik_driver"],
            "cgt_right_hip": ["cgt_right_shin_ik_driver", "cgt_right_foot_ik_driver"]
        }

        # references for setting drivers and constraints
        self.references = {
            # region DRIVERS
            # region arms
            "cgt_left_shoulder": [DriverType.limb_driver, self.driver_z_sca2loc_attr()],
            "cgt_left_wrist": self.arm_ik_driver_props("cgt_left_hand_ik_driver", self.left_arm_offset),
            "cgt_left_elbow": self.arm_ik_driver_props("cgt_left_forearm_ik_driver", self.left_arm_offset),
            "cgt_left_index": self.arm_ik_driver_props("cgt_left_index_ik_driver", self.left_arm_offset),

            "cgt_right_shoulder": [DriverType.limb_driver, self.driver_z_sca2loc_attr()],
            "cgt_right_wrist": self.arm_ik_driver_props("cgt_right_hand_ik_driver", self.right_arm_offset),
            "cgt_right_elbow": self.arm_ik_driver_props("cgt_right_forearm_ik_driver", self.right_arm_offset),
            "cgt_right_index": self.arm_ik_driver_props("cgt_right_index_ik_driver", self.right_arm_offset),

            # endregion
            # region legs
            "cgt_left_hip": [DriverType.limb_driver, self.driver_z_sca2loc_attr()],
            "cgt_left_knee": self.leg_ik_driver_props("cgt_left_shin_ik_driver", self.left_leg_offset),
            "cgt_left_ankle": self.leg_ik_driver_props("cgt_left_foot_ik_driver", self.left_leg_offset),

            "cgt_right_hip": [DriverType.limb_driver, self.driver_z_sca2loc_attr()],
            "cgt_right_knee": self.leg_ik_driver_props("cgt_right_shin_ik_driver", self.right_leg_offset),
            "cgt_right_ankle": self.leg_ik_driver_props("cgt_right_foot_ik_driver", self.right_leg_offset),
            # endregion
            # endregion

            # region CONSTRAINTS
            # region basic constraints
            "hip_center": [DriverType.constraint, ["torso", "COPY_ROTATION"]],
            "shoulder_center": [DriverType.constraint, ["chest", "COPY_ROTATION"]],
            # endregion

            # region arms (mapped mirrored)
            "cgt_left_hand_ik_driver": [DriverType.constraint, ["hand_ik.R", "COPY_LOCATION"]],
            "cgt_right_hand_ik_driver": [DriverType.constraint, ["hand_ik.L", "COPY_LOCATION"]],
            "cgt_left_forearm_ik_driver": [DriverType.constraint, ["forearm_tweak.R", "COPY_LOCATION"]],
            "cgt_right_forearm_ik_driver": [DriverType.constraint, ["forearm_tweak.L", "COPY_LOCATION"]],
            "cgt_left_index_ik_driver": [DriverType.constraint, ["hand_ik.R", "DAMPED_TRACK"]],
            "cgt_right_index_ik_driver": [DriverType.constraint, ["hand_ik.L", "DAMPED_TRACK"]],
            # endregion

            # region legs (mapped mirrored)
            # legs disables as they introduce major drifting issues
            # "cgt_right_foot_ik_driver": [DriverType.constraint, ["foot_ik.L", "COPY_LOCATION"]],
            # "cgt_left_foot_ik_driver": [DriverType.constraint, ["foot_ik.R", "COPY_LOCATION"]],
            # "cgt_left_shin_ik_driver": [DriverType.constraint, ["shin_tweak.R", "COPY_LOCATION"]],
            # "cgt_right_shin_ik_driver": [DriverType.constraint, ["shin_tweak.L", "COPY_LOCATION"]],
            # endregion
            # endregion
        }

        # setup relations between rig and drivers, then apply the drivers to the rig
        self.set_relation_dict(driver_objects)
        self.apply_drivers()

    # region rig driver relation setup
    def set_relation_dict(self, driver_objects: list):
        driver_names = [obj.name for obj in driver_objects]

        # dict containing drivers and required params
        for ref in self.references:
            if ref in driver_names:
                idx = driver_names.index(ref)
                driver_obj = driver_objects[idx]
                driver_type = self.references[ref][0]

                # multi user driver (scale driver)
                if ref in self.multi_user_driver_dict:
                    references = self.references[ref][1]    # driver properties
                    for t, driver_target in enumerate(self.multi_user_driver_dict[ref]):
                        refs = references.copy()    # copy driver properties to avoid overwrites
                        refs[0] = driver_target
                        rel = MappingRelation(driver_obj, driver_type, refs)
                        self.relation_mapping_lst.append(rel)

                # single user driver
                else:
                    relation = MappingRelation(driver_obj, driver_type, self.references[ref][1])
                    self.relation_mapping_lst.append(relation)
            else:
                print("Mapping failed for", ref, "in rigify_pose")

    # endregion

    # region apply drivers
    def apply_drivers(self):
        pose_bone_names = [bone.name for bone in self.pose_bones]

        for driver in self.relation_mapping_lst:
            values = driver.values[0]

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

    # endregion

    # region driver setup

    def arm_ik_driver_props(self, driver_target, offset):
        return [
            DriverType.limb_driver,
            self.driver_loc2loc_sca_attr(driver_target,
                                         offset,
                                         self.avg_arm_length)
        ]

    def leg_ik_driver_props(self, driver_target, offset):
        return [
            DriverType.limb_driver,
            self.driver_loc2loc_sca_attr(driver_target,
                                         offset,
                                         self.avg_arm_length)
        ]

    def get_avg_limb_length(self):
        avg_arm_length = self.get_average_scale(self.arm_bones, self.pose_bones)
        avg_leg_length = self.get_average_scale(self.leg_bones, self.pose_bones)
        return avg_arm_length, avg_leg_length

    def get_limb_offsets(self):
        left_arm_offset = self.get_location_offset(self.pose_bones, "upper_arm_ik.L", "cgt_right_shoulder")
        right_arm_offset = self.get_location_offset(self.pose_bones, "upper_arm_ik.R", "cgt_left_shoulder")

        left_leg_offset = self.get_location_offset(self.pose_bones, "thigh_ik.L", "cgt_right_hip")
        right_leg_offset = self.get_location_offset(self.pose_bones, "thigh_ik.R", "cgt_left_hip")
        return left_arm_offset, right_arm_offset, left_leg_offset, right_leg_offset

    @staticmethod
    def driver_z_sca2loc_attr():
        attribute = [
            None, "location", "scale",
            ["scale.z", "scale.z", "scale.z"],
            ["", "", ""]]
        return attribute

    @staticmethod
    def driver_loc2loc_sca_attr(driver_target, offset, avg_length):
        attribute = [
            driver_target, "location", "location",
            ["location.x", "location.y", "location.z"],
            [f"{offset[0]}+{avg_length}/(scale) *",
             f"{offset[1]}+{avg_length}/(scale) *",
             f"{offset[2]}+{avg_length}/(scale) *"]]
        return attribute
    # endregion
