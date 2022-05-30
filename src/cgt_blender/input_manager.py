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

from ..cgt_naming import COLLECTIONS
from .utils import objects


def transfer_animation():
    from .cgt_rig import rigify_pose, rigify_face
    from .cgt_rig import rigify_fingers

    col_mapping = {
        COLLECTIONS.hands: rigify_fingers.RigifyHands,
        COLLECTIONS.face:  rigify_face.RigifyFace,
        COLLECTIONS.pose:  rigify_pose.RigifyPose
    }

    user = bpy.context.scene.m_cgtinker_mediapipe

    selected_driver_collection = user.selected_driver_collection
    selected_armature = user.selected_rig.name_full

    print(f"TRYING TO TRANSFER ANIMATION DATA FROM {selected_driver_collection} TO {selected_armature}")

    driver_collections = objects.get_child_collections(selected_driver_collection)
    for col in driver_collections:
        armature = objects.get_armature(selected_armature)
        driver_objects = objects.get_objects_from_collection(col)
        col_mapping[col](armature, driver_objects)


def toggle_drivers():
    user = bpy.context.scene.m_cgtinker_mediapipe  # noqa
    user.toggle_drivers_bool = not user.toggle_drivers_bool
    print("toggled",  user.toggle_drivers_bool)

    driver_collections = objects.get_child_collections('CGT_DRIVERS')
    objs = objects.get_objects_from_collection('CGT_DRIVERS')
    print(objs)
    # objects.mute_driver(ob, user.toggle_drivers_bool)

