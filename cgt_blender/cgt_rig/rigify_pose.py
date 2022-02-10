from ...cgt_naming import POSE
from . import abs_rigging
from .abs_rigging import DriverType, MappingRelation
from .utils.drivers import limb_drivers
from ..utils import objects
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
        [POSE.shoulder_center,  POSE.left_shoulder],
        [POSE.left_shoulder,    POSE.left_elbow],
        [POSE.left_elbow,       POSE.left_wrist],
        [POSE.left_wrist,       POSE.left_index],

        [POSE.shoulder_center,  POSE.right_shoulder],
        [POSE.right_shoulder,   POSE.right_elbow],
        [POSE.right_elbow,      POSE.right_wrist],
        [POSE.right_wrist,      POSE.right_index]
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

        self.limb_drivers = [limb_drivers.LimbDriver(
            driver_target=driver,
            driver_origin=self.ik_driver_origins[idx],
            detected_joint=self.detected_joints[idx],
            rigify_joint_length=joint_lengths[idx],
            driver_offset=driver_offset[idx]
        ) for idx, driver in enumerate(self.driver_targets)]

        self.method_mapping = {
            DriverType.limb_driver: self.add_driver_batch,
            DriverType.constraint: self.add_constraint
        }

        # pose driver setup based on input cgt_rig
        for driver in self.limb_drivers:
            driver.set_expressions()

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
                driver_type = DriverType.limb_driver
                # add pose driver expressions to mapping list
                for expression in pose_driver.expressions:
                    relation = MappingRelation(driver_obj, driver_type, expression)
                    self.mapping_relation_list.append(relation)

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
    # endregion
