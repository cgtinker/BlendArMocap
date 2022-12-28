'''
Copyright (C) cgtinker, cgtinker.com, hello@cgtinker.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

import bpy

from .abs_rigging import BpyRigging
from . import face_drivers
from src.cgt_core.cgt_naming import FACE
from .rigify_naming import rigify_face_bone_names
from src.cgt_core.cgt_bpy import objects
from src.cgt_core.cgt_utils import cgt_math
import numpy as np


class RigifyFace(BpyRigging):
    """ Used for mapping values to drivers, holds rigify bone names and custom data names.
        Objects are getting searched by name, then drivers and constraints get applied. """

    def __init__(self, armature: bpy.types.Object, driver_objects: list):
        super().__init__(armature)
        bone_name_provider = rigify_face_bone_names.RigifyBoneNameProvider()
        bone_name_provider.update()

        # region constraints
        self.constraint_dict = {
            FACE.right_eye_t: [bone_name_provider.upper_lid_r, "COPY_LOCATION_OFFSET"],
            FACE.right_eye_b: [bone_name_provider.lower_lid_r, "COPY_LOCATION_OFFSET"],
            FACE.left_eye_t:  [bone_name_provider.upper_lid_l, "COPY_LOCATION_OFFSET"],
            FACE.left_eye_b:  [bone_name_provider.lower_lid_l, "COPY_LOCATION_OFFSET"],

            FACE.mouth_t:     [bone_name_provider.lip_t, "COPY_LOCATION_OFFSET"],
            FACE.mouth_b:     [bone_name_provider.lip_b, "COPY_LOCATION_OFFSET"],
            FACE.mouth_l:     [bone_name_provider.lip_r, "COPY_LOCATION_OFFSET"],
            FACE.mouth_r:     [bone_name_provider.lip_l, "COPY_LOCATION_OFFSET"],

            FACE.eyebrow_in_l:   [bone_name_provider.brow_in_r, "COPY_LOCATION_OFFSET"],
            # FACE.eyebrow_mid_l:  [bone_name_provider.brow_mid_r, "COPY_LOCATION_OFFSET"], # constrained by rigify
            FACE.eyebrow_out_l:  [bone_name_provider.brow_out_r, "COPY_LOCATION_OFFSET"],
            FACE.eyebrow_in_r:   [bone_name_provider.brow_in_l, "COPY_LOCATION_OFFSET"],
            # FACE.eyebrow_mid_r:  [bone_name_provider.brow_mid_l, "COPY_LOCATION_OFFSET"], # constrained by rigify
            FACE.eyebrow_out_r:  [bone_name_provider.brow_out_l, "COPY_LOCATION_OFFSET"],

            FACE.head:        [bone_name_provider.head_rot, "COPY_ROTATION_WORLD"],
            FACE.chin:        [bone_name_provider.jaw_rot, "COPY_ROTATION"],
        }
        # endregion

        # reset if overwrite
        bone_names = [pair[0] for key, pair in self.constraint_dict.items()]
        self.remove_bone_constraints(bone_names)

        # region eye drivers
        eye_driver_names = [[FACE.right_eye_t, FACE.right_eye_b], [FACE.left_eye_t, FACE.left_eye_b]]
        eye_dist_provider_objs = [FACE.right_eye, FACE.left_eye]
        eye_bone_names = [
            [bone_name_provider.upper_lid_r, bone_name_provider.lower_lid_r],
            [bone_name_provider.upper_lid_l, bone_name_provider.lower_lid_l]]
        rig_eye_distances = self.get_bone_distances(eye_bone_names)
        self.eye_drivers = face_drivers.EyeDriverContainer(
            eye_driver_names, eye_dist_provider_objs, rig_eye_distances, eye_bone_names)
        # endregion

        # region mouth drivers
        mouth_driver_names = [[FACE.mouth_t, FACE.mouth_b], [FACE.mouth_r, FACE.mouth_l]]
        mouth_bone_names = [[bone_name_provider.lip_t, bone_name_provider.lip_b],
                            [bone_name_provider.lip_r, bone_name_provider.lip_l]]
        mouth_provider_objs = [FACE.mouth, FACE.mouth_corners]
        mouth_distances = self.get_bone_distances(mouth_bone_names)
        self.mouth_drivers = face_drivers.MouthDriverContainer(
            mouth_driver_names, mouth_provider_objs, mouth_distances, mouth_bone_names)
        # endregion

        # region eyebrow drivers
        eyebrow_provider_objs = [FACE.left_eyebrow, FACE.right_eyebrow]
        eyebrow_bone_names = [
            [bone_name_provider.brow_in_r, bone_name_provider.forehead_in_r],
            # [bone_name_provider.brow_mid_r, bone_name_provider.forehead_mid_r],
            [bone_name_provider.brow_out_r, bone_name_provider.forehead_out_r],
            [bone_name_provider.brow_in_l, bone_name_provider.forehead_in_l],
            # [bone_name_provider.brow_mid_l, bone_name_provider.forehead_mid_l],
            [bone_name_provider.brow_out_l, bone_name_provider.forehead_out_l]]
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

        self.apply_driver([self.eye_drivers, self.mouth_drivers, self.eyebrow_drivers])
        self.apply_constraints(self.constraint_dict)

    def get_bone_distances(self, bone_pairs):
        # get distance between bones
        objects.set_mode('EDIT')
        joints = [[self.edit_bone_head(joint[0]), self.edit_bone_head(joint[1])] for joint in bone_pairs]
        # must calc distances within edit mode (func requires nesting)
        distances = [cgt_math.get_vector_distance(np.array(joint[0]), np.array(joint[1])) for joint in joints]
        objects.set_mode('OBJECT')
        return distances
