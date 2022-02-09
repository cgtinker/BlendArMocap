import os
from dataclasses import dataclass

# has to be at root
PACKAGE = os.path.basename(os.path.dirname(__file__))
ADDON_NAME = "BlendArMocap"


@dataclass(frozen=True, init=False)
class COLLECTIONS:
    drivers = "cgt_DRIVERS"
    hands = "cgt_HANDS"
    face = "cgt_FACE"
    pose = "cgt_POSE"


@dataclass(frozen=True, init=False)
class POSE:
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
    left_shoulder = "CGT_LEFT_SHOULDER"
    right_shoulder = "CGT_RIGHT_SHOULDER"
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
    left_hip = "CGT_LEFT_HIP"
    right_hip = "CGT_RIGHT_HIP"
    left_knee = "cgt_left_knee"
    right_knee = "cgt_right_knee"
    left_ankle = "cgt_left_ankle"
    right_ankle = "cgt_right_ankle"
    left_heel = "cgt_left_heel"
    right_heel = "cgt_right_heel"
    left_foot_index = "cgt_left_foot_index"
    right_foot_index = "cgt_right_foot_index"

    # DIVERS
    hip_center = "CGT_HIP_CENTER_DRIVER"
    shoulder_center = "CGT_SHOULDER_CENTER_DRIVER"

    left_shoulder_ik = "CGT_LEFT_SHOULDER_IK_DRIVER"
    right_shoulder_ik = "CGT_RIGHT_SHOULDER_IK_DRIVER"
    left_forearm_ik = "CGT_LEFT_FOREARM_IK_DRIVER"
    right_forearm_ik = "CGT_RIGHT_FOREARM_IK_DRIVER"
    left_hand_ik = "CGT_LEFT_HAND_IK_DRIVER"
    right_hand_ik = "CGT_RIGHT_HAND_IK_DRIVER"
    left_index_ik = "CGT_LEFT_INDEX_IK_DRIVER"
    right_index_ik = "CGT_RIGHT_INDEX_IK_DRIVER"

    left_hip_ik = "CGT_LEFT_HIP_IK_DRIVER"
    right_hip_ik = "CGT_RIGHT_HIP_IK_DRIVER"
    right_foot_ik = "CGT_RIGHT_FOOT_IK_DRIVER"
    left_foot_ik = "CGT_LEFT_FOOT_IK_DRIVER"
    left_shin_ik = "CGT_LEFT_SHIN_IK_DRIVER"
    right_shin_ik = "CGT_RIGHT_SHIN_IK_DRIVER"


@dataclass(frozen=True, init=False)
class HAND:
    wrist = "CGT_WRIST"
    thumb_cmc = "CGT_THUMB_CMC"
    thumb_mcp = "CGT_THUMB_MCP"
    thumb_ip = "CGT_THUMP_IP"
    thumb_tip = "CGT_THUMB_TIP"
    index_finger_mcp = "CGT_INDEX_FINGER_MCP"
    index_finger_pip = "CGT_INDEX_FINGER_PIP"
    index_finger_dip = "CGT_INDEX_FINGER_DIP"
    index_finger_tip = "CGT_INDEX_FINGER_TIP"
    middle_finger_mcp = "CGT_MIDDLE_FINGER_MCP"
    middle_finger_pip = "CGT_MIDDLE_FINGER_PIP"
    middle_finger_dip = "CGT_MIDDLE_FINGER_DIP"
    middle_finger_tip = "CGT_MIDDLE_FINGER_TIP"
    ring_finger_mcp = "CGT_RING_FINGER_MCP"
    ring_finger_pip = "CGT_RING_FINGER_PIP"
    ring_finger_dip = "CGT_RING_FINGER_DIP"
    ring_finger_tip = "CGT_RING_FINGER_TIP"
    pinky_mcp = "CGT_PINKY_MCP"
    pinky_pip = "CGT_PINKY_PIP"
    pinky_dip = "CGT_PINKY_DIP"
    pinky_tip = "CGT_PINKY_TIP"


@dataclass(frozen=True, init=False)
class FACE:
    face = "cgt_face_empty_"

    head = "CGT_FACE_ROTATION"
    chin = "CGT_CHIN_ROTATION"
    mouth = "CGT_MOUTH_DRIVER"
    left_eye = "CGT_LEFT_EYE_DRIVER"
    right_eye = "CGT_RIGHT_EYE_DRIVER"
    right_eyebrow = "CGT_RIGHT_EYEBROW_DRIVER"
    left_eyebrow = "CGT_LEFT_EYEBROW_DRIVER"

    right_eye_t = "CGT_RIGHT_EYE_DRIVER_T"
    right_eye_b = "CGT_RIGHT_EYE_DRIVER_B"
    left_eye_t = "CGT_LEFT_EYE_DRIVER_T"
    left_eye_b = "CGT_LEFT_EYE_DRIVER_B"
    mouth_t = "CGT_MOUTH_DRIVER_T"
    mouth_b = "CGT_MOUTH_DRIVER_B"
    mouth_r = "CGT_MOUTH_DRIVER_R"
    mouth_l = "CGT_MOUTH_DRIVER_L"

    eyebrow_in_l = "CGT_EYEBROW_IN_L"
    eyebrow_mid_l = "CGT_EYEBROW_MID_L"
    eyebrow_out_l = "CGT_EYEBROW_OUT_L"

    eyebrow_in_r = "CGT_EYEBROW_IN_R"
    eyebrow_mid_r = "CGT_EYEBROW_MID_R"
    eyebrow_out_r = "CGT_EYEBROW_OUT_R"
