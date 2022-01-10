import importlib
from enum import Enum

from blender import objects, abs_rigging
from utils import m_V

importlib.reload(m_V)
importlib.reload(objects)
importlib.reload(abs_rigging)


class DriverType(Enum):
    arm_driver = 0
    constraint = 1


class MappingRelation:
    source = None
    values = None
    diver_type = None

    def __init__(self, source, driver_type: DriverType, *args):
        self.source = source
        self.driver_type = driver_type
        self.values = args


class RigPose(abs_rigging.BpyRigging):
    def __init__(self, armature, driver_objects: list):
        self.relation_dict = {}
        self.relation_mapping_lst = []
        self.extension = ""

        self.method_mapping = {
            # todo: arm specific driver method
            DriverType.arm_driver: self.add_driver_batch,
            DriverType.constraint: self.add_constraint
        }

        self.pose_bones = armature.pose.bones
        self.arm_bones = [
            ["upper_arm_fk.L", "forearm_fk.L"],
            ["forearm_fk.L", "hand_fk.L"],

            ["upper_arm_fk.R", "forearm_fk.R"],
            ["forearm_fk.R", "hand_fk.R"],
        ]

        self.avg_arm_length = self.get_average_scale(self.arm_bones, self.pose_bones)

        self.references = {
            "cgt_left_shoulder": [
                DriverType.arm_driver, [
                        None, "location", "scale",
                        ["scale.z", "scale.z", "scale.z"],
                        ["", "", ""]
                    ]
            ],

            "cgt_left_wrist": [
                DriverType.arm_driver, [
                    "cgt_hand_ik_driver", "location", "location",
                    ["location.x", "location.y", "location.z"],
                    [f"{self.avg_arm_length}/(scale) *",
                     f"{self.avg_arm_length}/(scale) *",
                     f"1 + {self.avg_arm_length}/(scale) *"]
                ]
            ],

            "cgt_left_elbow": [
                DriverType.arm_driver, [
                    "cgt_forearm_ik_driver", "location", "location",
                    ["location.x", "location.y", "location.z"],
                    [f"{self.avg_arm_length}/(scale) *",
                     f"{self.avg_arm_length}/(scale) *",
                     f"1+{self.avg_arm_length}/(scale) *"]
                ]
            ],

            "hip_center": [DriverType.constraint, ["hips", "COPY_ROTATION"]],
            "shoulder_center": [DriverType.constraint, ["chest", "COPY_ROTATION"]],
            "cgt_forearm_ik_driver": [DriverType.constraint, ["forearm_tweak.R", "COPY_LOCATION"]]
        }

        self.set_relation_dict(driver_objects)
        self.apply_drivers(armature)

    def set_relation_dict(self, driver_objects: list):
        driver_names = [obj.name for obj in driver_objects]
        for ref in self.references:
            if ref in driver_names:
                idx = driver_names.index(ref)
                driver_obj = driver_objects[idx]
                driver_type = self.references[ref][0]

                if ref == "cgt_left_shoulder":
                    # shoulder driver is required multiple times
                    references = self.references[ref][1]
                    references[0] = "cgt_hand_ik_driver"
                    relation = MappingRelation(driver_obj, driver_type, references)
                    self.relation_mapping_lst.append(relation)

                    references[0] = "cgt_forearm_ik_driver"
                    relation = MappingRelation(driver_obj, driver_type, references)
                    self.relation_mapping_lst.append(relation)

                else:
                    relation = MappingRelation(driver_obj, driver_type, self.references[ref][1])
                    self.relation_mapping_lst.append(relation)
            else:
                print("Mapping failed for", ref, "in rigify_pose")

    def apply_drivers(self, armature):
        pose_bone_names = [bone.name for bone in self.pose_bones]

        for driver in self.relation_mapping_lst:
            values = driver.values[0]

            if driver.driver_type == DriverType.arm_driver:
                target = objects.get_object_by_name(values[0])

                # add_driver_batch(driver_target, driver_source, prop_source, prop_target, data_path, func)
                add_driver_batch = self.method_mapping[driver.driver_type]
                add_driver_batch(target, driver.source, values[1], values[2], values[3], values[4])
                print("DRIVER:", driver.driver_type, target, driver.source, values[1], values[2], values[3], values[4])

            elif driver.driver_type == DriverType.constraint:
                if values[0] in pose_bone_names:
                    idx = pose_bone_names.index(values[0])
                    pose_bone = self.pose_bones[idx]
                    # add_constraint(bone, target, constraint)
                    add_constraint = self.method_mapping[driver.driver_type]
                    add_constraint(pose_bone, driver.source, values[1])
