import os
from enum import Enum

# has to be at root
PACKAGE = os.path.basename(os.path.dirname(__file__))
ADDON_NAME = "BlendArMocap"


class Pose(Enum):
    collection = "cgt_pose"
    
    nose = "cgt_nose"
    left_eye_inner = "cgt_left_eye_inner"
    left_eye = "cgt_left_eye"
    left_eye_outer = "cgt_left_eye_outer"
    right_eye_inner = "cgt_right_eye_inner"
    right_eye = "cgt_right_eye"
    right_eye_outer = "cgt_right_eye_outer"
    left_ear = "cgt_left_ear"
    right_ear = "cgt_right_ear"
    mouth_left = "cgt_mouth_left"
    mouth_right = "cgt_mouth_right"
    left_shoulder = "cgt_left_shoulder"
    right_shoulder = "cgt_right_shoulder"
    left_elbow = "cgt_left_elbow"
    right_elbow = "cgt_right_elbow"
    left_wrist = "cgt_left_wrist"
    right_wrist = "cgt_right_wrist"
    left_pinky = "cgt_left_pinky"
    right_pinky = "cgt_right_pinky"
    left_index = "cgt_left_index"
    right_index = "cgt_right_index"
    left_thumb = "cgt_left_thumb"
    right_thumb = "cgt_right_thumb"
    left_hip = "cgt_left_hip"
    right_hip = "cgt_right_hip"
    left_knee = "cgt_left_knee"
    right_knee = "cgt_right_knee"
    left_ankle = "cgt_left_ankle"
    right_ankle = "cgt_right_ankle"
    left_heel = "cgt_left_heel"
    right_heel = "cgt_right_heel"
    left_foot_index = "cgt_left_foot_index"
    right_foot_index = "cgt_right_foot_index"

    # DIVERS
    left_forearm_ik = "cgt_left_forearm_ik_driver"
    right_forearm_ik = "cgt_right_forearm_ik_driver"
    left_hand_ik = "cgt_left_hand_ik_driver"
    right_hand_ik = "cgt_right_hand_ik_driver"
    left_index_ik = "cgt_left_index_ik_driver"
    right_index_ik = "cgt_right_index_ik_driver"

    right_foot_ik = "cgt_right_foot_ik_driver"
    left_foot_ik = "cgt_left_foot_ik_driver"
    left_shin_ik = "cgt_left_shin_ik_driver"
    right_shin_ik = "cgt_right_shin_ik_driver"


class Hand(Enum):
    collection = "cgt_hands"

    wrist = "cgt_WRIST"
    thumb_cmc = "cgt_THUMB_CMC"
    thumb_mcp = "cgt_THUMB_MCP"
    thumb_ip = "cgt_THUMP_IP"
    thumb_tip = "cgt_THUMB_TIP"
    index_finger_mcp = "cgt_INDEX_FINGER_MCP"
    index_finger_pip = "cgt_INDEX_FINGER_PIP"
    index_finger_dip = "cgt_INDEX_FINGER_DIP"
    index_finger_tip = "cgt_INDEX_FINGER_TIP"
    middle_finger_mcp = "cgt_MIDDLE_FINGER_MCP"
    middle_finger_pip = "cgt_MIDDLE_FINGER_PIP"
    middle_finger_dip = "cgt_MIDDLE_FINGER_DIP"
    middle_finger_tip = "cgt_MIDDLE_FINGER_TIP"
    ring_finger_mcp = "cgt_RING_FINGER_MCP"
    ring_finger_pip = "cgt_RING_FINGER_PIP"
    ring_finger_dip = "cgt_RING_FINGER_DIP"
    ring_finger_tip = "cgt_RING_FINGER_TIP"
    pinky_mcp = "cgt_PINKY_MCP"
    pinky_pip = "cgt_PINKY_PIP"
    pinky_dip = "cgt_PINKY_DIP"
    pinky_tip = "cgt_PINKY_TIP"


class Face(Enum):
    collection = "cgt_face"
    face = "cgt_face_empty_"

    head = "face_rotation"
    chin = "chin_rotation"
    mouth = "mouth_driver"
    left_eye = "left_eye_driver"
    right_eye = "right_eye_driver"
    right_eyebrow = "right_eyebrow_driver"
    left_eyebrow = "left_eyebrow_driver"

    right_eye_t = "right_eye_driver_T"
    right_eye_b = "right_eye_driver_B"
    left_eye_t = "left_eye_driver_T"
    left_eye_b = "left_eye_driver_B"
    mouth_t = "mouth_driver_T"
    mouth_b = "mouth_driver_B"
    mouth_r = "mouth_driver_R"
    mouth_l = "mouth_driver_L"

    eyebrow_in_l = "eyebrow_in_l"
    eyebrow_mid_l = "eyebrow_mid_l"
    eyebrow_out_l = "eyebrow_out_l"

    eyebrow_in_r = "eyebrow_in_r"
    eyebrow_mid_r = "eyebrow_mid_r"
    eyebrow_out_r = "eyebrow_out_r"
