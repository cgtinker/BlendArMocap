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

import os
from dataclasses import dataclass


# has to be at root
PACKAGE = os.path.basename(os.path.dirname(os.path.dirname(__file__)))
print(PACKAGE, "- add-on path:", os.path.dirname(os.path.dirname(__file__)))
ADDON_NAME = "BlendArMocap_freemocap"


@dataclass(frozen=True, init=False)
class COLLECTIONS:
    drivers = "cgt_DRIVERS"
    hands = "cgt_HANDS"
    face = "cgt_FACE"
    pose = "cgt_POSE"


@dataclass(frozen=True, init=False)
class POSE:
    nose = "cgt_nose"
    left_eye_inner = "cgt_eye_inner.L"
    left_eye = "cgt_eye.L"
    left_eye_outer = "cgt_eye_outer.L"
    right_eye_inner = "cgt_eye_inner.R"
    right_eye = "cgt_eye.R"
    right_eye_outer = "cgt_eye_outer.R"
    left_ear = "cgt_ear.L"
    right_ear = "cgt_ear.R"
    mouth_left = "cgt_left.L"
    mouth_right = "cgt_mouth.R"
    left_shoulder = "cgt_shoulder.L"
    right_shoulder = "cgt_shoulder.R"
    left_elbow = "cgt_elbow.L"
    right_elbow = "cgt_elbow.R"
    left_wrist = "cgt_pose_wrist.L"
    right_wrist = "cgt_pose_wrist.R"
    left_pinky = "cgt_pinky.L"
    right_pinky = "cgt_pinky.R"
    left_index = "cgt_index.L"
    right_index = "cgt_index.R"
    left_thumb = "cgt_thumb.L"
    right_thumb = "cgt_thumb.R"
    left_hip = "cgt_hip.L"
    right_hip = "cgt_hip.R"
    left_knee = "cgt_knee.L"
    right_knee = "cgt_knee.R"
    left_ankle = "cgt_ankle.L"
    right_ankle = "cgt_ankle.R"
    left_heel = "cgt_heel.L"
    right_heel = "cgt_heel.R"
    left_foot_index = "cgt_foot_index.L"
    right_foot_index = "cgt_foot_index.R"

    # DIVERS
    hip_center = "cgt_hip_center"
    shoulder_center = "cgt_shoulder_center"

    shoulder_center_ik = "cgt_shoulder_center_driver"
    left_shoulder_ik = "cgt_shoulder_driver.L"
    right_shoulder_ik = "cgt_shoulder_driver.R"
    left_forearm_ik = "cgt_forearm_driver.L"
    right_forearm_ik = "cgt_forearm_driver.R"
    left_hand_ik = "cgt_hand_driver.L"
    right_hand_ik = "cgt_hand_driver.R"
    left_index_ik = "cgt_index_driver.L"
    right_index_ik = "cgt_index_driver.R"

    hip_center_ik = "cgt_hip_center_driver"
    left_hip_ik = "cgt_hip_driver.L"
    right_hip_ik = "cgt_hip_driver.R"
    left_shin_ik = "cgt_shin_driver.L"
    right_shin_ik = "cgt_shin_driver.R"
    left_foot_ik = "cgt_foot_driver.L"
    right_foot_ik = "cgt_foot_driver.R"
    left_foot_index_ik = "cgt_foot_index_driver.L"
    right_foot_index_ik = "cgt_foot_index_driver.R"


@dataclass(frozen=True, init=False)
class HAND:
    wrist = "cgt_wrist"
    thumb_cmc = "cgt_thumb_cmc"
    thumb_mcp = "cgt_thumb_mcp"
    thumb_ip = "cgt_thump_ip"
    thumb_tip = "cgt_thumb_tip"
    index_finger_mcp = "cgt_index_mcp"
    index_finger_pip = "cgt_index_pip"
    index_finger_dip = "cgt_index_dip"
    index_finger_tip = "cgt_index_tip"
    middle_finger_mcp = "cgt_middle_mcp"
    middle_finger_pip = "cgt_middle_pip"
    middle_finger_dip = "cgt_middle_dip"
    middle_finger_tip = "cgt_middle_tip"
    ring_finger_mcp = "cgt_ring_mcp"
    ring_finger_pip = "cgt_ring_pip"
    ring_finger_dip = "cgt_ring_dip"
    ring_finger_tip = "cgt_ring_tip"
    pinky_mcp = "cgt_pinky_mcp"
    pinky_pip = "cgt_pinky_pip"
    pinky_dip = "cgt_pinky_dip"
    pinky_tip = "cgt_pinky_tip"

    driver_thumb_cmc = "cgt_thumb_cmc_driver"
    driver_thumb_mcp = "cgt_thumb_mcp_driver"
    driver_thumb_ip = "cgt_thump_ip_driver"
    driver_thumb_tip = "cgt_thumb_tip_driver"
    driver_index_finger_mcp = "cgt_index_mcp_driver"
    driver_index_finger_pip = "cgt_index_pip_driver"
    driver_index_finger_dip = "cgt_index_dip_driver"
    driver_index_finger_tip = "cgt_index_tip_driver"
    driver_middle_finger_mcp = "cgt_middle_mcp_driver"
    driver_middle_finger_pip = "cgt_middle_pip_driver"
    driver_middle_finger_dip = "cgt_middle_dip_driver"
    driver_middle_finger_tip = "cgt_middle_tip_driver"
    driver_ring_finger_mcp = "cgt_ring_mcp_driver"
    driver_ring_finger_pip = "cgt_ring_pip_driver"
    driver_ring_finger_dip = "cgt_ring_dip_driver"
    driver_ring_finger_tip = "cgt_ring_tip_driver"
    driver_pinky_mcp = "cgt_pinky_mcp_driver"
    driver_pinky_pip = "cgt_pinky_pip_driver"
    driver_pinky_dip = "cgt_pinky_dip_driver"
    driver_pinky_tip = "cgt_pinky_tip_driver"


@dataclass(frozen=True, init=False)
class FACE:
    face = "cgt_face_vertex_"

    head = "cgt_face_rotation"
    chin = "cgt_chin_rotation"
    mouth = "cgt_mouth_driver"
    mouth_corners = "cgt_mouth_corner_driver"
    left_eye = "cgt_eye_driver.L"
    right_eye = "cgt_eye_driver.R"
    right_eyebrow = "cgt_eyebrow_driver.R"
    left_eyebrow = "cgt_eyebrow_driver.L"

    right_eye_t = "cgt_eye_driver.T.R"
    right_eye_b = "cgt_eye_driver.B.R"
    left_eye_t = "cgt_eye_driver.T.L"
    left_eye_b = "cgt_eye_driver.B.L"
    mouth_t = "cgt_mouth_driver.T"
    mouth_b = "cgt_mouth_driver.B"
    mouth_r = "cgt_mouth_driver.R"
    mouth_l = "cgt_mouth_driver.L"

    eyebrow_in_l = "cgt_eyebrow.I.L"
    eyebrow_mid_l = "cgt_eyebrow.M.L"
    eyebrow_out_l = "cgt_eyebrow.O.L"

    eyebrow_in_r = "cgt_eyebrow.I.R"
    eyebrow_mid_r = "cgt_eyebrow.M.R"
    eyebrow_out_r = "cgt_eyebrow.O.R"
