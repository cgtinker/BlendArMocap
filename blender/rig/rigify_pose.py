import m_CONST
from blender.rig import abs_rigging
from blender.rig.abs_rigging import DriverType, MappingRelation
from blender.utils import objects
from utils import m_V


class RigifyPose(abs_rigging.BpyRigging):
    arm_bone_names = [
        # left arm
        ["upper_arm_fk.L", "forearm_fk.L"],
        ["forearm_fk.L", "hand_fk.L"],
        ["hand_fk.L", "f_middle.01_master.L"],
        # right arm
        ["upper_arm_fk.R", "forearm_fk.R"],
        ["forearm_fk.R", "hand_fk.R"],
        ["hand_fk.R", "f_middle.01_master.R"]

    ]
    # bone chain lengths:
    left_upper_arm_length, left_fore_arm_length, left_wrist_length = .0, .0, .0
    right_upper_arm_length, right_fore_arm_length, right_wrist_length = .0, .0, .0

    # bone offsets:
    left_shoulder_offset, left_elbow_offset, left_wrist_offset = .0, .0, .0
    right_shoulder_offset, right_elbow_offset, right_wrist_offset = .0, .0, .0

    leg_bone_names = [
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
        # self.avg_arm_length, self.avg_leg_length = self.get_avg_limb_length()
        self.get_arm_joint_lengths()
        self.get_arm_offsets()

        """
        m_CONST.POSE.left_hand_ik.value,
        m_CONST.POSE.left_forearm_ik.value,
        m_CONST.POSE.left_index_ik.value
        """
        self.multi_user_driver_dict = {
            m_CONST.POSE.left_elbow.value:
                [
                    self.set_ik_driver_scale_attr(
                        m_CONST.POSE.left_shoulder.value
                    ),
                    self.set_ik_driver_expression(
                        m_CONST.POSE.left_forearm_ik.value,
                        self.left_shoulder_offset,
                        self.left_upper_arm_length
                    )
                ],
            m_CONST.POSE.left_wrist.value:
                [
                    self.set_ik_driver_scale_attr(
                        m_CONST.POSE.left_elbow.value
                    ),
                    self.set_ik_driver_expression(
                        m_CONST.POSE.left_hand_ik.value,
                        self.left_elbow_offset,
                        self.left_wrist_length
                    )],
            m_CONST.POSE.left_index.value:
                [
                    self.set_ik_driver_scale_attr(
                        m_CONST.POSE.left_wrist.value
                    ),
                    self.set_ik_driver_expression(
                        m_CONST.POSE.left_index_ik.value,
                        self.left_wrist_offset,
                        self.left_wrist_length
                    )],

            # right arm
            m_CONST.POSE.right_elbow.value:
                [
                    self.set_ik_driver_scale_attr(
                        m_CONST.POSE.right_shoulder.value
                    ),
                    self.set_ik_driver_expression(
                        m_CONST.POSE.right_forearm_ik.value,
                        self.right_shoulder_offset,
                        self.right_upper_arm_length
                    )],
            m_CONST.POSE.right_wrist.value:
                [
                    self.set_ik_driver_scale_attr(
                        m_CONST.POSE.right_elbow.value
                    ),
                    self.set_ik_driver_expression(
                        m_CONST.POSE.right_hand_ik.value,
                        self.right_elbow_offset,
                        self.right_wrist_length
                    )],
            m_CONST.POSE.right_index.value:
                [
                    self.set_ik_driver_scale_attr(
                        m_CONST.POSE.right_wrist.value
                    ),
                    self.set_ik_driver_expression(
                        m_CONST.POSE.right_index_ik.value,
                        self.right_wrist_offset,
                        self.left_wrist_length
                    )],
        }

        # references for setting drivers and m_CONSTraints
        self.references = {
            # region DRIVERS
            # region arms
            # left arm
            m_CONST.POSE.left_elbow.value: [DriverType.limb_driver],
            m_CONST.POSE.left_wrist.value: [DriverType.limb_driver],
            m_CONST.POSE.left_index.value: [DriverType.limb_driver],

            m_CONST.POSE.right_elbow.value: [DriverType.limb_driver],
            m_CONST.POSE.right_wrist.value: [DriverType.limb_driver],
            m_CONST.POSE.right_index.value: [DriverType.limb_driver],
            # region m_CONSTRAINTS
            # region basic constraints
            m_CONST.POSE.hip_center.value: [DriverType.constraint, ["torso", "COPY_ROTATION"]],
            m_CONST.POSE.shoulder_center.value: [DriverType.constraint, ["chest", "COPY_ROTATION"]],
            # endregion

            # region arms (mapped mirrored)
            m_CONST.POSE.left_hand_ik.value: [DriverType.constraint, ["hand_ik.R", "COPY_LOCATION"]],
            m_CONST.POSE.right_hand_ik.value: [DriverType.constraint, ["hand_ik.L", "COPY_LOCATION"]],
            m_CONST.POSE.left_forearm_ik.value: [DriverType.constraint, ["forearm_tweak.R", "COPY_LOCATION"]],
            m_CONST.POSE.right_forearm_ik.value: [DriverType.constraint, ["forearm_tweak.L", "COPY_LOCATION"]],
            m_CONST.POSE.left_index_ik.value: [DriverType.constraint, ["hand_ik.R", "DAMPED_TRACK"]],
            m_CONST.POSE.right_index_ik.value: [DriverType.constraint, ["hand_ik.L", "DAMPED_TRACK"]],
            # endregion

            # region legs (mapped mirrored)
            # legs disables as they introduce major drifting issues
            # "cgt_right_foot_ik_driver": [DriverType.m_CONSTraint, ["foot_ik.L", "COPY_LOCATION"]],
            # "cgt_left_foot_ik_driver": [DriverType.m_CONSTraint, ["foot_ik.R", "COPY_LOCATION"]],
            # "cgt_left_shin_ik_driver": [DriverType.m_CONSTraint, ["shin_tweak.R", "COPY_LOCATION"]],
            # "cgt_right_shin_ik_driver": [DriverType.m_CONSTraint, ["shin_tweak.L", "COPY_LOCATION"]],
            # endregion
            # endregion
        }

        # setup relations between rig and drivers, then apply the drivers to the rig
        self.set_relation_dict(driver_objects)
        # self.apply_drivers()

    # region rig driver relation setup
    def set_relation_dict(self, driver_objects: list):
        driver_names = [obj.name for obj in driver_objects]

        # dict containing drivers and required params
        for ref in self.references:
            if ref in driver_names:
                idx = driver_names.index(ref)
                driver_obj = driver_objects[idx]
                driver_type = self.references[ref][0]
                print(ref, idx)
                # multi user driver (scale driver)
                if ref in self.multi_user_driver_dict:
                    print(ref)
                    for expression in self.multi_user_driver_dict[ref]:
                        rel = MappingRelation(driver_obj, driver_type, expression)
                        self.relation_mapping_lst.append(rel)
                        print(rel, "\n")
                    # references = self.references[ref][1]  # driver properties
                    # for t, driver_target in enumerate(self.multi_user_driver_dict[ref]):
                    #     refs = references.copy()  # copy driver properties to avoid overwrites
                    #     refs[0] = driver_target
                    #     rel = MappingRelation(driver_obj, driver_type, refs)
                    #     self.relation_mapping_lst.append(rel)

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
    def get_arm_joint_lengths(self):
        """ length of individual arm joints """
        arm_bones = self.get_joints(self.arm_bone_names, self.pose_bones)
        self.left_upper_arm_length = m_V.get_vector_distance(arm_bones[0][0], arm_bones[0][1])
        self.left_fore_arm_length = m_V.get_vector_distance(arm_bones[1][0], arm_bones[1][1])
        self.left_wrist_length = m_V.get_vector_distance(arm_bones[2][0], arm_bones[2][1])

        self.right_upper_arm_length = m_V.get_vector_distance(arm_bones[3][0], arm_bones[3][1])
        self.right_fore_arm_length = m_V.get_vector_distance(arm_bones[4][0], arm_bones[4][1])
        self.right_wrist_length = m_V.get_vector_distance(arm_bones[5][0], arm_bones[5][1])

    def get_arm_offsets(self):
        """ offset for individual arm joints """
        self.left_shoulder_offset = self.get_location_offset(
            self.pose_bones, "upper_arm_ik.L", m_CONST.POSE.right_shoulder.value)
        self.left_elbow_offset = self.get_location_offset(
            self.pose_bones, "forearm_tweak.L", m_CONST.POSE.right_elbow.value)
        self.left_wrist_offset = self.get_location_offset(
            self.pose_bones, "hand_ik.L", m_CONST.POSE.right_wrist.value)

        self.right_shoulder_offset = self.get_location_offset(
            self.pose_bones, "upper_arm_ik.R", m_CONST.POSE.right_shoulder.value)
        self.right_elbow_offset = self.get_location_offset(
            self.pose_bones, "forearm_tweak.R", m_CONST.POSE.right_elbow.value)
        self.right_wrist_offset = self.get_location_offset(
            self.pose_bones, "hand_ik.R", m_CONST.POSE.right_wrist.value)

    def set_ik_driver_expression(self, driver_target, offset, joint_length):
        return self.driver_loc2loc_sca_attr(driver_target,
                                            offset,
                                            joint_length)

    def set_ik_driver_scale_attr(self, target):
        return self.driver_z_sca2loc_attr(target)

    @staticmethod
    def driver_z_sca2loc_attr(target):
        attribute = [
            target, "location", "scale",
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
