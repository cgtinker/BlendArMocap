import bpy

from .abs_rigging import BpyRigging
from .utils.drivers.face_drivers import EyeDriverContainer, MouthDriverContainer
from ...cgt_naming import FACE


class RigifyFace(BpyRigging):
    def __init__(self, armature: bpy.types.Object, driver_objects: list):
        self.pose_bones = armature.pose.bones

        # eye drivers
        eye_driver_names = [[FACE.right_eye_t, FACE.right_eye_b], [FACE.left_eye_t, FACE.left_eye_b]]
        eye_dist_provider_objs = [FACE.right_eye, FACE.left_eye]
        eye_bone_names = [
            ["lid.T.R.002", "lid.B.R.002"],
            ["lid.T.L.002", "lid.B.L.002"]]
        rig_eye_distances = self.get_bone_distances(eye_bone_names)
        self.eye_drivers = EyeDriverContainer(eye_driver_names,
                                              eye_dist_provider_objs,
                                              rig_eye_distances)

        # mouth driversa
        mouth_driver_names = [[FACE.mouth_t, FACE.mouth_b], [FACE.mouth_r, FACE.mouth_l]]
        mouth_bone_names = [["lip.T", "lip.B"], ["lips.R", "lips.L"]]
        mouth_provider_obj = FACE.mouth
        mouth_distances = self.get_bone_distances(mouth_bone_names)
        self.mouth_drivers = MouthDriverContainer(mouth_driver_names,
                                                  mouth_provider_obj,
                                                  mouth_distances)

        # constraints
        self.constraints = {
            FACE.right_eye_t: ["lid.T.R.002", "COPY_LOCATION_OFFSET"],
            FACE.right_eye_b: ["lid.B.R.002", "COPY_LOCATION_OFFSET"],

            FACE.left_eye_t:  ["lid.T.L.002", "COPY_LOCATION_OFFSET"],
            FACE.left_eye_b:  ["lid.B.L.002", "COPY_LOCATION_OFFSET"],

            # FACE.mouth_t:     [DriverType.CONSTRAINT, ["lip.T", "COPY_LOCATION_OFFSET"]],
            # FACE.mouth_b:     [DriverType.CONSTRAINT, ["lip.B", "COPY_LOCATION_OFFSET"]],
            #
            # FACE.mouth_l:     [DriverType.CONSTRAINT, ["lips.R", "COPY_LOCATION_OFFSET"]],
            # FACE.mouth_r:     [DriverType.CONSTRAINT, ["lips.L", "COPY_LOCATION_OFFSET"]],

            FACE.head:        ["head", "COPY_ROTATION_WORLD"],
            FACE.chin:        ["jaw_master", "COPY_ROTATION"],
            # endregion
        }

        self.set_relation_dict(driver_objects)
        self.apply_drivers()

    def set_relation_dict(self, driver_objects):
        driver_names = [obj.name for obj in driver_objects]

        self.set_single_prop_relation([self.eye_drivers, self.mouth_drivers], driver_names, driver_objects)
        self.set_constraint_relation(self.constraints, driver_names, driver_objects)

    def get_bone_distances(self, bone_pairs):
        distances = []
        for pair in bone_pairs:
            avg_scale = self.get_average_joint_bone_length([pair], self.pose_bones)
            distances.append(avg_scale)

        return distances
