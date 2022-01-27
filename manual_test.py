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

import importlib

import bpy

from bridge import pose_drivers
from utils import m_V

importlib.reload(m_V)
importlib.reload(pose_drivers)

references = {
    0: "cgt_nose",
    1: "cgt_left_eye_inner",
    2: "cgt_left_eye",
    3: "cgt_left_eye_outer",
    4: "cgt_right_eye_inner",
    5: "cgt_right_eye",
    6: "cgt_right_eye_outer",
    7: "cgt_left_ear",
    8: "cgt_right_ear",
    9: "cgt_mouth_left",
    10: "cgt_mouth_right",
    11: "cgt_left_shoulder",
    12: "cgt_right_shoulder",
    13: "cgt_left_elbow",
    14: "cgt_right_elbow",
    15: "cgt_left_wrist",
    16: "cgt_right_wrist",
    17: "cgt_left_pinky",
    18: "cgt_right_pinky",
    19: "cgt_left_index",
    20: "cgt_right_index",
    21: "cgt_left_thumb",
    22: "cgt_right_thumb",
    23: "cgt_left_hip",
    24: "cgt_right_hip",
    25: "cgt_left_knee",
    26: "cgt_right_knee",
    27: "cgt_left_ankle",
    28: "cgt_right_ankle",
    29: "cgt_left_heel",
    30: "cgt_right_heel",
    31: "cgt_left_foot_index",
    32: "cgt_right_foot_index",
    33: "shoulder_center",
    34: "hip_center"
}


def get_empty_obj(index: int):
    obj = bpy.data.objects[references[index]]
    return obj


def get_empty_loc(index: int):
    obj = bpy.data.objects[references[index]].location
    return obj


def main(model, frame):
    landmark_data = [[idx, get_empty_loc(idx)] for idx in range(33)]
    update(model, landmark_data, frame)


def update(model, data, frame):
    model.data = data
    model.frame = frame
    model.init_data()
    model.update()


if __name__ == '__main__':
    model = pose_drivers.BridgePose()
    model.pose = [get_empty_obj(idx) for idx in range(33)]
    model.shoulder_center.obj = get_empty_obj("shoulder_center")
    model.shoulder_center.idx = 33
    model.hip_center.obj = get_empty_obj("hip_center")
    model.hip_center.idx = 34
    frame = 8
    main(model, frame)
