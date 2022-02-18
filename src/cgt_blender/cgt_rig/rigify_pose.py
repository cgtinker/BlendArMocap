from . import abs_rigging
from .abs_rigging import DriverType, MappingRelation
from .utils.drivers import limb_driver_expressions
from ..utils import objects
from ...cgt_naming import POSE
from ...cgt_utils import m_V


class RigifyPose(abs_rigging.BpyRigging):
    pose_constraints = {
        # plain copy rotation
        POSE.hip_center:       ["torso", "COPY_ROTATION"],
        POSE.shoulder_center:  ["chest", "COPY_ROTATION"],

        # copy pose driver location
        POSE.left_hand_ik:     ["hand_ik.R", "COPY_LOCATION"],
        POSE.right_hand_ik:    ["hand_ik.L", "COPY_LOCATION"],
        POSE.left_forearm_ik:  ["forearm_tweak.R", "COPY_LOCATION"],
        POSE.right_forearm_ik: ["forearm_tweak.L", "COPY_LOCATION"],

        # damped track to pose driver
        POSE.left_index_ik:    ["hand_ik.R", "DAMPED_TRACK"],
        POSE.right_index_ik:   ["hand_ik.L", "DAMPED_TRACK"]
    }

    driver_targets = [
        POSE.left_shoulder_ik, POSE.left_forearm_ik,
        POSE.left_hand_ik, POSE.left_index_ik,
        POSE.right_shoulder_ik, POSE.right_forearm_ik,
        POSE.right_hand_ik, POSE.right_index_ik
    ]

    shoulder_center = ["upper_arm_fk.R", "upper_arm_fk.L"]
    hip_center = ["", ""]
    rigify_joints = [
        ["shoulder_center", "upper_arm_fk.R"], ["upper_arm_fk.R", "forearm_fk.R"],
        ["forearm_fk.R", "hand_fk.R"], ["hand_fk.R", "f_middle.01_master.R"],

        ["shoulder_center", "upper_arm_fk.L"], ["upper_arm_fk.L", "forearm_fk.L"],
        ["forearm_fk.L", "hand_fk.L"], ["hand_fk.L", "f_middle.01_master.L"],
    ]

    ik_driver_origins = [
        POSE.shoulder_center, POSE.left_shoulder_ik,
        POSE.left_forearm_ik, POSE.left_hand_ik,

        POSE.shoulder_center, POSE.right_shoulder_ik,
        POSE.right_forearm_ik, POSE.right_hand_ik,
    ]

    detected_joints = [
        [POSE.shoulder_center, POSE.left_shoulder],
        [POSE.left_shoulder, POSE.left_elbow],
        [POSE.left_elbow, POSE.left_wrist],
        [POSE.left_wrist, POSE.left_index],

        [POSE.shoulder_center, POSE.right_shoulder],
        [POSE.right_shoulder, POSE.right_elbow],
        [POSE.right_elbow, POSE.right_wrist],
        [POSE.right_wrist, POSE.right_index]
    ]

    mapping_relation_list = []

    def __init__(self, armature, driver_objects: list):
        self.pose_bones = armature.pose.bones

        self.shoulder_center = self.get_rigify_shoulder_center()
        self.hip_center = None
        joint_lengths = self.get_rigify_joint_lengths()

        driver_offset = [
            self.shoulder_center, None, None, None,
            self.shoulder_center, None, None, None
        ]
        # NEW DRIVER EXPRESSION SETUP
        self.limb_drivers = [limb_driver_expressions.LimbDriver(
            driver_target=target,
            driver_origin=self.ik_driver_origins[idx],
            detected_joint=self.detected_joints[idx],
            rigify_joint_length=joint_lengths[idx],
            driver_offset=driver_offset[idx]
        ) for idx, target in enumerate(self.driver_targets)]

        self.method_mapping = {
            DriverType.constraint:  self.add_constraint,
            DriverType.single_prop: self.add_single_prop_driver
        }

        self.set_relation_dict(driver_objects)
        self.apply_drivers()

    def get_rigify_shoulder_center(self):
        def pos(bone_name):
            return self.pose_bones[bone_name].head

        center = m_V.center_point(pos(self.shoulder_center[0]), pos(self.shoulder_center[1]))
        return center

    def get_rigify_joint_lengths(self):
        """ return the lengths of given joints while it uses
            center as keyword for a custom joint origin based on the first index """

        def pos(bone_name):
            return self.pose_bones[bone_name].head

        joint_lengths = []
        for joint in self.rigify_joints:
            if "shoulder_center" in joint:
                joint_locs = [self.shoulder_center, pos(joint[1])]
            elif "hip_center" in joint:
                joint_locs = [self.hip_center, pos(joint[1])]
            else:
                joint_locs = [pos(name) for name in joint]
            length = m_V.get_vector_distance(joint_locs[0], joint_locs[1])
            joint_lengths.append(length)
        return joint_lengths

    # region mapping relation setup
    def set_relation_dict(self, driver_objects: list):
        """ Sets a list of relations for further data transfer. """
        driver_names = [obj.name for obj in driver_objects]
        self.add_pose_driver_mapping(driver_names, driver_objects)
        self.add_constraint_mapping(driver_names, driver_objects)

    def add_pose_driver_mapping(self, driver_names, driver_objects):
        def setup_relation(pose_driver):
            if pose_driver.provider_obj in driver_names:
                # get the provider object by name
                driver_obj = self.get_driver_object(pose_driver.provider_obj, driver_names, driver_objects)
                # create a mapping relation
                relation = MappingRelation(driver_obj, pose_driver.driver_type, pose_driver)
                self.mapping_relation_list.append(relation)

        # setup drivers
        for drivers in self.limb_drivers:
            for driver in drivers.pose_drivers:
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
        """ applies all mapping relations for mapping values
            gets target method by driver type."""
        pose_bone_names = [bone.name for bone in self.pose_bones]

        def apply_by_type(values):
            print(mapping_relation.driver_type)
            if mapping_relation.driver_type == DriverType.constraint:
                print("attempt to apply constraint")
                if values[0] in pose_bone_names:
                    # get bone
                    idx = pose_bone_names.index(values[0])
                    pose_bone = self.pose_bones[idx]
                    # add constraint to bone
                    add_constraint = self.method_mapping[mapping_relation.driver_type]
                    add_constraint(pose_bone, mapping_relation.source, values[1])

            elif mapping_relation.driver_type == DriverType.single_prop:
                print("attempt to apply single prop drivers")
                # get target object
                driver = values
                driver.target_object = objects.get_object_by_name(values.target_object)
                driver.provider_obj = mapping_relation.source
                # add driver to object
                single_prop_driver = self.method_mapping[mapping_relation.driver_type]
                single_prop_driver(driver)

        for mapping_relation in self.mapping_relation_list:
            apply_by_type(mapping_relation.values)
    # endregion
    # endregion
