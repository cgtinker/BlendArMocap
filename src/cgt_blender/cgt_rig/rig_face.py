from ...cgt_naming import FACE
from .abs_rigging import BpyRigging
from .utils.mapping import MappingRelation
from ..utils import objects
from .utils.drivers.driver_interface import DriverType
import bpy


class RigifyFace(BpyRigging):
    relation_mapping_lst = []

    eye_bone_names = [["lid.T.R.002", "lid.B.R.002"], ["lid.T.L.002", "lid.B.L.002"]]
    eye_driver_names = [[FACE.right_eye_t, FACE.right_eye_b],
                        [FACE.left_eye_t, FACE.left_eye_b]]

    def __init__(self, armature: bpy.types.Object, driver_objects: list):
        self.pose_bones = armature.pose.bones

        eye_distances = self.get_bone_distances(self.eye_bone_names)

        # types for mapping
        self.method_mapping = {
            DriverType.LIMB:        self.add_driver_batch,
            DriverType.CONSTRAINT:  self.add_constraint,
            DriverType.face_driver: self.add_driver_batch
        }

        # drivers are getting used multiple times
        self.multi_user_driver_dict = {
            FACE.right_eye: [
                [self.eye_driver_names[0][0], eye_distances[0], self.eye_top_down_dir_driver_attr],
                [self.eye_driver_names[0][1], eye_distances[0], self.eye_up_dir_driver_attr]],
            FACE.left_eye:  [
                [self.eye_driver_names[1][0], eye_distances[1], self.eye_top_down_dir_driver_attr],
                [self.eye_driver_names[1][1], eye_distances[1], self.eye_up_dir_driver_attr]],
        }

        # mapping may contains multi user drivers
        self.references = {
            # region main drivers
            FACE.mouth:       [DriverType.face_driver],
            FACE.left_eye:    [DriverType.face_driver],
            FACE.right_eye:   [DriverType.face_driver],

            FACE.right_eye_t: [DriverType.CONSTRAINT, ["lid.T.R.002", "COPY_LOCATION_OFFSET"]],
            FACE.right_eye_b: [DriverType.CONSTRAINT, ["lid.B.R.002", "COPY_LOCATION_OFFSET"]],

            FACE.left_eye_t:  [DriverType.CONSTRAINT, ["lid.T.L.002", "COPY_LOCATION_OFFSET"]],
            FACE.left_eye_b:  [DriverType.CONSTRAINT, ["lid.B.L.002", "COPY_LOCATION_OFFSET"]],

            FACE.mouth_t:     [DriverType.CONSTRAINT, ["lip.T", "COPY_LOCATION_OFFSET"]],
            FACE.mouth_b:     [DriverType.CONSTRAINT, ["lip.B", "COPY_LOCATION_OFFSET"]],

            FACE.mouth_l:     [DriverType.CONSTRAINT, ["lips.R", "COPY_LOCATION_OFFSET"]],
            FACE.mouth_r:     [DriverType.CONSTRAINT, ["lips.L", "COPY_LOCATION_OFFSET"]],
            # TODO: FACE ROTATION HAS TO APPLIED TO WORLD SPACE
            FACE.head:        [DriverType.CONSTRAINT, ["head", "COPY_ROTATION_WORLD"]],
            FACE.chin:        [DriverType.CONSTRAINT, ["jaw_master", "COPY_ROTATION"]],
            # endregion
        }

        self.set_relation_mapping_list(driver_objects)
        self.apply_drivers()

    def set_relation_mapping_list(self, driver_objects: list):
        driver_names = [obj.name for obj in driver_objects]

        def get_driver_obj_and_type_by_ref_name(ref_name):
            idx = driver_names.index(ref_name)
            m_obj = driver_objects[idx]
            m_type = self.references[ref_name][0]
            return m_obj, m_type

        def set_multi_user_driver_data(driver_obj, driver_type, ref_name):
            for driver_target in self.multi_user_driver_dict[ref_name]:
                attribute_function = driver_target[2]
                refs = attribute_function(driver_target[0], driver_target[1])
                rel = MappingRelation(driver_obj, driver_type, refs)
                self.relation_mapping_lst.append(rel)

        def set_single_user_driver_data(driver_obj, driver_type, ref_name):
            relation = MappingRelation(driver_obj, driver_type, self.references[ref_name][1])
            self.relation_mapping_lst.append(relation)

        def set_driver_data(ref_name):
            driver_obj, driver_type = get_driver_obj_and_type_by_ref_name(ref_name)
            if ref_name not in self.multi_user_driver_dict:
                set_single_user_driver_data(driver_obj, driver_type, ref_name)
            else:
                set_multi_user_driver_data(driver_obj, driver_type, ref_name)

        for reference_name in self.references:
            if reference_name in driver_names:
                set_driver_data(reference_name)
            else:
                print(f"Mapping failed for {reference_name} in rigify_face")

    def apply_drivers(self):
        pose_bone_names = [bone.name for bone in self.pose_bones]

        for driver in self.relation_mapping_lst:
            values = driver.values[0]

            if driver.driver_type == DriverType.face_driver:
                target = objects.get_object_by_name(values[0])
                add_driver_batch = self.method_mapping[driver.driver_type]
                add_driver_batch(target, driver.source, values[1], values[2], values[3], values[4])

            elif driver.driver_type == DriverType.CONSTRAINT:
                print(driver)
                if values[0] in pose_bone_names:
                    idx = pose_bone_names.index(values[0])
                    pose_bone = self.pose_bones[idx]

                    add_constraint = self.method_mapping[driver.driver_type]
                    add_constraint(pose_bone, driver.source, values[1])

    # endregion

    @staticmethod
    def get_target_axis(axis):
        """target only a specifc scale axis"""
        target_axis = []
        for tar_axis in ["X", "Y", "Z"]:
            if tar_axis == axis:
                target_axis.append("scale." + tar_axis.lower())
            else:
                target_axis.append("")

        return target_axis

    @staticmethod
    def get_loc_sca_driver_attribute(target, target_axis, functions):
        attribute = [
            target, "location", "scale",
            target_axis,
            functions]
        return attribute

    def get_bone_location_offsets(self, bone_names, driver_names):
        offsets = []
        for idx in range(2):
            pair = [[bone_names[idx][i], driver_names[idx][i]] for i in range(2)]
            offset = [self.get_location_offset(self.pose_bones, p[0], p[1]) for p in pair]
            offsets.append(offset)

        return offsets

    def get_bone_distances(self, bone_pairs):
        distances = []
        for pair in bone_pairs:
            avg_scale = self.get_average_joint_bone_length([pair], self.pose_bones)
            distances.append(avg_scale)

        return distances
