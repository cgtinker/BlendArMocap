import bpy

from .abs_rigging import BpyRigging
from .utils.drivers import face_drivers
from ...cgt_naming import FACE


class RigifyFace(BpyRigging):
    def __init__(self, armature: bpy.types.Object, driver_objects: list):
        super().__init__(armature)

        # region eye drivers
        eye_driver_names = [[FACE.right_eye_t, FACE.right_eye_b], [FACE.left_eye_t, FACE.left_eye_b]]
        eye_dist_provider_objs = [FACE.right_eye, FACE.left_eye]
        eye_bone_names = [
            ["lid.T.R.002", "lid.B.R.002"],
            ["lid.T.L.002", "lid.B.L.002"]]
        rig_eye_distances = self.get_bone_distances(eye_bone_names)
        self.eye_drivers = face_drivers.EyeDriverContainer(
            eye_driver_names, eye_dist_provider_objs, rig_eye_distances, eye_bone_names)
        # endregion

        # region mouth drivers
        mouth_driver_names = [[FACE.mouth_t, FACE.mouth_b], [FACE.mouth_r, FACE.mouth_l]]
        mouth_bone_names = [["lip.T", "lip.B"], ["lips.R", "lips.L"]]
        mouth_provider_objs = [FACE.mouth, FACE.mouth_corners]
        mouth_distances = self.get_bone_distances(mouth_bone_names)
        self.mouth_drivers = face_drivers.MouthDriverContainer(
            mouth_driver_names, mouth_provider_objs, mouth_distances, mouth_bone_names)
        # endregion

        # region eyebrow drivers
        eyebrow_provider_objs = [FACE.left_eyebrow, FACE.right_eyebrow]
        eyebrow_bone_names = [
            ["brow.T.R.003", "DEF-forehead.R"],  # ["brow.T.R.002", "DEF-forehead.R.001"],
            ["brow.T.R.001", "DEF-forehead.R.002"],
            ["brow.T.L.003", "DEF-forehead.L"],  # ["brow.T.L.002", "DEF-forehead.L.001"],
            ["brow.T.L.001", "DEF-forehead.L.002"]]
        eyebrow_distances = self.get_bone_distances(eyebrow_bone_names)
        eyebrow_driver_names = [
            FACE.eyebrow_in_l,  # FACE.eyebrow_mid_l,
            FACE.eyebrow_out_l,
            FACE.eyebrow_in_r,  # FACE.eyebrow_mid_r,
            FACE.eyebrow_out_r]
        _eyebrow_bone_names = [name[0] for name in eyebrow_bone_names]
        self.eyebrow_drivers = face_drivers.EyebrowDriverContainer(
            eyebrow_driver_names, eyebrow_provider_objs, eyebrow_distances, _eyebrow_bone_names
        )
        # endregion

        # region constraints
        self.constraint_dict = {
            FACE.right_eye_t: [eye_bone_names[0][0], "COPY_LOCATION_OFFSET"],
            FACE.right_eye_b: [eye_bone_names[0][1], "COPY_LOCATION_OFFSET"],
            FACE.left_eye_t:  [eye_bone_names[1][0], "COPY_LOCATION_OFFSET"],
            FACE.left_eye_b:  [eye_bone_names[1][1], "COPY_LOCATION_OFFSET"],

            FACE.mouth_t:     [mouth_bone_names[0][0], "COPY_LOCATION_OFFSET"],
            FACE.mouth_b:     [mouth_bone_names[0][1], "COPY_LOCATION_OFFSET"],
            FACE.mouth_l:     [mouth_bone_names[1][0], "COPY_LOCATION_OFFSET"],
            FACE.mouth_r:     [mouth_bone_names[1][1], "COPY_LOCATION_OFFSET"],

            FACE.eyebrow_in_l:   [eyebrow_bone_names[0][0], "COPY_LOCATION_OFFSET"],
            # FACE.eyebrow_mid_l:  [eyebrow_bone_names[1][0], "COPY_LOCATION_OFFSET"], # constrained by rigify
            FACE.eyebrow_out_l:  [eyebrow_bone_names[1][0], "COPY_LOCATION_OFFSET"],
            FACE.eyebrow_in_r:   [eyebrow_bone_names[2][0], "COPY_LOCATION_OFFSET"],
            # FACE.eyebrow_mid_r:  [eyebrow_bone_names[4][0], "COPY_LOCATION_OFFSET"], # constrained by rigify
            FACE.eyebrow_out_r:  [eyebrow_bone_names[3][0], "COPY_LOCATION_OFFSET"],

            FACE.head:        ["head", "COPY_ROTATION_WORLD"],
            FACE.chin:        ["jaw_master", "COPY_ROTATION"],
            # endregion
        }
        # endregion

        self.n_apply_driver([self.eye_drivers, self.mouth_drivers, self.eyebrow_drivers])
        self.n_apply_constraints(self.constraint_dict)

    def get_bone_distances(self, bone_pairs):
        distances = []
        for pair in bone_pairs:
            avg_scale = self.get_average_joint_bone_length([pair], self.pose_bones)
            distances.append(avg_scale)

        return distances
