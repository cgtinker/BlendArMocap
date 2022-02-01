import importlib

from _blender.rig.abs_rigging import DriverType, MappingRelation, BpyRigging
from _blender.utils import objects
from utils import log
import m_CONST

importlib.reload(m_CONST)
importlib.reload(objects)


class RigifyFace(BpyRigging):
    relation_mapping_lst = []

    eye_bone_names = [["lid.T.R.002", "lid.B.R.002"], ["lid.T.L.002", "lid.B.L.002"]]
    eye_driver_names = [[m_CONST.FACE.right_eye_t.value, m_CONST.FACE.right_eye_b.value],
                        [m_CONST.FACE.left_eye_t.value, m_CONST.FACE.left_eye_b.value]]

    mouth_bone_names = [["lip.T", "lip.B"], ["lips.R", "lips.L"]]
    mouth_driver_names = [[m_CONST.FACE.mouth_t.value, m_CONST.FACE.mouth_b.value],
                          [m_CONST.FACE.mouth_r.value, m_CONST.FACE.mouth_l.value]]

    # eyebrow_bone_names = [
    #     ["brow.T.R.003", "DEF-forehead.R"], ["brow.T.R.002", "DEF-forehead.R.001"],
    #     ["brow.T.R.001", "DEF-forehead.R.002"],

    #     ["brow.T.L.003", "DEF-forehead.L"], ["brow.T.L.002", "DEF-forehead.L.001"],
    #     ["brow.T.L.001", "DEF-forehead.L.002"]]
    # eyebrow_driver_names = [
    #     m_CONST.FACE.eyebrow_in_l.value, m_CONST.FACE.eyebrow_mid_l.value, m_CONST.FACE.eyebrow_out_l.value,
    #     m_CONST.FACE.eyebrow_in_r.value, m_CONST.FACE.eyebrow_mid_r.value, m_CONST.FACE.eyebrow_out_r.value]

    def __init__(self, armature, driver_objects: list):
        self.pose_bones = armature.pose.bones

        eye_distances = self.get_bone_distances(self.eye_bone_names)
        mouth_distances = self.get_bone_distances(self.mouth_bone_names)
        # eyebrow_distances = self.get_bone_distances(self.eyebrow_bone_names)

        # types for mapping
        self.method_mapping = {
            DriverType.limb_driver: self.add_driver_batch,
            DriverType.constraint: self.add_constraint,
            DriverType.face_driver: self.add_driver_batch
        }

        # drivers are getting used multiple times
        self.multi_user_driver_dict = {
            m_CONST.FACE.right_eye.value: [
                [self.eye_driver_names[0][0], eye_distances[0], self.eye_top_down_dir_driver_attr],
                [self.eye_driver_names[0][1], eye_distances[0], self.eye_up_dir_driver_attr]],
            m_CONST.FACE.left_eye.value: [
                [self.eye_driver_names[1][0], eye_distances[1], self.eye_top_down_dir_driver_attr],
                [self.eye_driver_names[1][1], eye_distances[1], self.eye_up_dir_driver_attr]],

            m_CONST.FACE.mouth.value: [
                [self.mouth_driver_names[0][0], mouth_distances[0], self.mouth_up_dir_driver_attr],
                [self.mouth_driver_names[0][1], mouth_distances[0], self.mouth_down_dir_driver_attr],
                [self.mouth_driver_names[1][0], mouth_distances[1], self.mouth_left_dir_driver_attr],
                [self.mouth_driver_names[1][1], mouth_distances[1], self.mouth_right_dir_driver_attr]
            ],

            # m_CONST.FACE.left_eyebrow.value: [
            #     [self.eyebrow_driver_names[0], eyebrow_distances[0], self.eyebrow_driver_attr],
            #     [self.eyebrow_driver_names[1], eyebrow_distances[1], self.eyebrow_driver_attr],
            #     [self.eyebrow_driver_names[2], eyebrow_distances[2], self.eyebrow_driver_attr],
            # ],
            # m_CONST.FACE.right_eyebrow.value: [
            #     [self.eyebrow_driver_names[3], eyebrow_distances[3], self.eyebrow_driver_attr],
            #     [self.eyebrow_driver_names[4], eyebrow_distances[4], self.eyebrow_driver_attr],
            #     [self.eyebrow_driver_names[5], eyebrow_distances[5], self.eyebrow_driver_attr],
            # ],
        }

        # mapping may contains multi user drivers
        self.references = {
            # region main drivers
            m_CONST.FACE.mouth.value: [DriverType.face_driver],
            m_CONST.FACE.left_eye.value: [DriverType.face_driver],
            m_CONST.FACE.right_eye.value: [DriverType.face_driver],
            # m_CONST.FACE.right_eyebrow.value: [DriverType.face_driver],
            # m_CONST.FACE.left_eyebrow.value: [DriverType.face_driver],
            # endregion

            # region m_CONSTraints
            # "eyebrow_in_l": [DriverType.m_CONSTraint, [self.eyebrow_bone_names[0][0], "COPY_LOCATION_OFFSET"]],
            # "eyebrow_mid_l":    [DriverType.m_CONSTraint, [self.eyebrow_bone_names[1][0],    "COPY_LOCATION_OFFSET"]],
            # "eyebrow_out_l": [DriverType.m_CONSTraint, [self.eyebrow_bone_names[2][0], "COPY_LOCATION_OFFSET"]],
            # "eyebrow_in_r": [DriverType.m_CONSTraint, [self.eyebrow_bone_names[3][0], "COPY_LOCATION_OFFSET"]],
            # "eyebrow_mid_r":    [DriverType.m_CONSTraint, [self.eyebrow_bone_names[4][0],    "COPY_LOCATION_OFFSET"]],
            # "eyebrow_out_r": [DriverType.m_CONSTraint, [self.eyebrow_bone_names[5][0], "COPY_LOCATION_OFFSET"]],

            m_CONST.FACE.right_eye_t.value: [DriverType.constraint, ["lid.T.R.002", "COPY_LOCATION_OFFSET"]],
            m_CONST.FACE.right_eye_b.value: [DriverType.constraint, ["lid.B.R.002", "COPY_LOCATION_OFFSET"]],

            m_CONST.FACE.left_eye_t.value: [DriverType.constraint, ["lid.T.L.002", "COPY_LOCATION_OFFSET"]],
            m_CONST.FACE.left_eye_b.value: [DriverType.constraint, ["lid.B.L.002", "COPY_LOCATION_OFFSET"]],

            m_CONST.FACE.mouth_t.value: [DriverType.constraint, ["lip.T", "COPY_LOCATION_OFFSET"]],
            m_CONST.FACE.mouth_b.value: [DriverType.constraint, ["lip.B", "COPY_LOCATION_OFFSET"]],

            m_CONST.FACE.mouth_l.value: [DriverType.constraint, ["lips.R", "COPY_LOCATION_OFFSET"]],
            m_CONST.FACE.mouth_r.value: [DriverType.constraint, ["lips.L", "COPY_LOCATION_OFFSET"]],

            m_CONST.FACE.head.value: [DriverType.constraint, ["head", "COPY_ROTATION"]],
            m_CONST.FACE.chin.value: [DriverType.constraint, ["jaw_master", "COPY_ROTATION"]],
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
            print(reference_name)
            if reference_name in driver_names:
                set_driver_data(reference_name)
                print("found_reference")
            else:
                log.logger.debug(f"Mapping failed for {reference_name} in rigify_face")

    def apply_drivers(self):
        pose_bone_names = [bone.name for bone in self.pose_bones]

        for driver in self.relation_mapping_lst:
            values = driver.values[0]

            if driver.driver_type == DriverType.face_driver:
                target = objects.get_object_by_name(values[0])
                add_driver_batch = self.method_mapping[driver.driver_type]
                add_driver_batch(target, driver.source, values[1], values[2], values[3], values[4])

            elif driver.driver_type == DriverType.constraint:
                print(driver)
                if values[0] in pose_bone_names:
                    idx = pose_bone_names.index(values[0])
                    pose_bone = self.pose_bones[idx]

                    add_constraint = self.method_mapping[driver.driver_type]
                    add_constraint(pose_bone, driver.source, values[1])

    def eyebrow_driver_attr(self, target, avg_distance):
        axis = "Z"
        axis_dict = {
            "in": "X",
            "mid": "Y",
            "out": "Z"
        }
        # check if target contains name (driver vals are mapped to specific axis)
        axis = [v for k, v in axis_dict.items() if k in target][0]
        functions = ["", "", f"{avg_distance}*.2*"]
        attribute = self.get_loc_sca_driver_attribute(target, ["", "", "scale." + axis.lower()], functions)
        print(target, attribute)
        return attribute

    # region eyes
    def eye_up_dir_driver_attr(self, target, avg_distance):
        functions = ["", "", f"-{avg_distance}*.25*"]
        attribute = self.get_loc_sca_driver_attribute(target, self.get_target_axis("Z"), functions)
        return attribute

    def eye_top_down_dir_driver_attr(self, target, avg_distance):
        functions = ["", "", f"-{avg_distance}*.65+{avg_distance}*"]
        attribute = self.get_loc_sca_driver_attribute(target, self.get_target_axis("Z"), functions)
        return attribute

    # endregion

    # region mouth
    def get_mouth_driver_attr(self, driver_attr, target, avg_distance):
        mouth_attr_dict = {
            "up": [".3", "Z"],
            "down": ["-.3", "Z"],
            "left": [".05", "X"],
            "right": ["-.05", "X"]
        }
        factor, axis = mouth_attr_dict[driver_attr]
        return self.mouth_scale_driver_attr(target, avg_distance, factor, axis)

    def mouth_up_dir_driver_attr(self, target, avg_distance):
        return self.get_mouth_driver_attr("up", target, avg_distance)

    def mouth_down_dir_driver_attr(self, target, avg_distance):
        return self.get_mouth_driver_attr("down", target, avg_distance)

    def mouth_left_dir_driver_attr(self, target, avg_distance):
        return self.get_mouth_driver_attr("left", target, avg_distance)

    def mouth_right_dir_driver_attr(self, target, avg_distance):
        return self.get_mouth_driver_attr("right", target, avg_distance)

    def mouth_scale_driver_attr(self, target, avg_distance, factor, axis):
        functions = []
        for tar_axis in ["X", "Y", "Z"]:
            if tar_axis == axis:
                func = f"{avg_distance}*{factor}*"
            else:
                func = ""
            functions.append(func)

        attribute = self.get_loc_sca_driver_attribute(target, self.get_target_axis(axis), functions)
        return attribute

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
