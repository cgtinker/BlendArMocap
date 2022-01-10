import importlib

from blender import objects, abs_rigging
from utils import m_V

importlib.reload(m_V)
importlib.reload(objects)
importlib.reload(abs_rigging)


class MappingRelation:
    target = None
    values = None

    def __init__(self, target, *args):
        self.target = target
        self.values = args


class RigPose(abs_rigging.BpyRigging):
    def __init__(self, armature, driver_objects):
        self.relation_dict = {}
        self.extension = ""

        self.references = {
            # empty_references name: [
            #     "Empty_Target", "DRIVER", "prop_source", "prop_target",
            #     data-paths["x", "y", "z"], func["x", "y", "z"]
            # ]
            # test empty overwrites name thats whats happinin
            "cgt_left_shoulder": ["Test_Empty", "DRIVER", self.set_shoulder_driver],
            "cgt_left_wrist": ["Test_Empty", "DRIVER", self.set_wrist_driver],

            # cd pose empty name:       [pose_bone.name,        constraint,         None]
            "hip_center": ["hips", "COPY_ROTATION", None],
            "shoulder_center": ["chest", "COPY_ROTATION", None],
        }

        self.arm_bones = [
            ["upper_arm_fk.L", "forearm_fk.L"],
            ["forearm_fk.L", "hand_fk.L"],

            ["upper_arm_fk.R", "forearm_fk.R"],
            ["forearm_fk.R", "hand_fk.R"],
        ]
        self.set_relation_dict(driver_objects)
        self.apply_drivers(armature)

    def set_shoulder_driver(self, driver_target, driver_source):
        print("setting shoulder drive")
        self.add_driver_batch(
            driver_target=driver_target, driver_source=driver_source,
            prop_source="scale", prop_target="scale",
            data_path=["scale.z", "scale.z", "scale.z"], func=["", "", ""])

        self.add_driver_batch(
            driver_target=driver_target, driver_source=driver_source,
            prop_source="location", prop_target="scale",
            data_path=["scale.z", "scale.z", "scale.z"], func=["", "", ""])

    def set_wrist_driver(self, driver_target, driver_source):
        print("setting wrist")
        self.add_driver_batch(
            driver_target=driver_target, driver_source=driver_source,
            prop_source="location", prop_target="location",
            data_path=["location.x", "location.y", "location.z"], func=["", "", ""])

    def set_relation_dict(self, driver_objects):
        driver_names = [obj.name for obj in driver_objects]
        relations = []
        for ref in self.references:
            if ref in driver_names:
                idx = driver_names.index(ref)
                driver_obj = driver_objects[idx]
                relation = MappingRelation(driver_obj, self.references[ref])
                relations.append(relation)
            else:
                print("Mapping failed for", ref, "in rigify_pose")
        print(relations)
        for empty in driver_objects:
            try:
                bone_name = self.references[empty.name][0]
                if bone_name != None:
                    print("bone name added", bone_name)
                    refs = [r for r in self.references[empty.name]]
                    refs.append(empty)

                    self.relation_dict[bone_name] = refs

            except KeyError:
                pass

    def apply_drivers(self, armature):
        pose_bones = armature.pose.bones
        avg_arm_scale = self.get_average_scale(self.arm_bones, pose_bones)

        for key, value in self.relation_dict.items():
            # todo: improve readability
            print("in process", value)
            if value[1] not in self.constraint_mapping:
                print(value)
                # len-2 = method to run, value[0] contains tar obj name, value len-1 contains driver source
                value[len(value) - 2](objects.get_object_by_name(value[0]), value[len(value) - 1])

                print("should add driver")
                pass
            else:
                self.add_constraint(bone=pose_bones[key], target=value[len(value) - 1], constraint=value[1])
