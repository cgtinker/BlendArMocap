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

            FACE.head:        [DriverType.CONSTRAINT, ["head", "COPY_ROTATION_WORLD"]],
            FACE.chin:        [DriverType.CONSTRAINT, ["jaw_master", "COPY_ROTATION"]],
            # endregion
        }

        self.set_relation_dict(driver_objects)
        self.apply_drivers()

    def set_relation_dict(self, driver_object):
        pass

    def get_bone_distances(self, bone_pairs):
        distances = []
        for pair in bone_pairs:
            avg_scale = self.get_average_joint_bone_length([pair], self.pose_bones)
            distances.append(avg_scale)

        return distances
