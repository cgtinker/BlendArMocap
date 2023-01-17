import os
import logging
from dataclasses import dataclass
from .cgt_utils.cgt_json import JsonData
from pathlib import Path

# has to be at root
PACKAGE = os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))
logging.getLogger("BlendArMocap").debug(f"{PACKAGE}, {os.path.dirname(os.path.dirname(__file__))}")
ADDON_NAME = "BlendArMocap"


class CGTDefaultsJson(JsonData):
    pose: dict
    face: dict
    hand: dict
    identifier: str

    def __init__(self):
        path = Path(__file__).parent / "cgt_defaults.json"
        super().__init__(str(path))


cgt_defaults = CGTDefaultsJson()


@dataclass(frozen=True, init=True)
class COLLECTIONS:
    """ TODO: Store all dataclasses as json in dicts - positions matter therefore this setup aint practical
        todo: !!!
        """
    drivers: str = "cgt_DRIVERS"
    hands: str = "cgt_HAND"
    face: str = "cgt_FACE"
    pose: str = "cgt_POSE"


@dataclass(frozen=True, init=False)
class POSE:
    nose: str = "cgt_nose"
    left_eye_inner: str = "cgt_eye_inner.L"
    left_eye: str = "cgt_eye.L"
    left_eye_outer: str = "cgt_eye_outer.L"
    right_eye_inner: str = "cgt_eye_inner.R"
    right_eye: str = "cgt_eye.R"
    right_eye_outer: str = "cgt_eye_outer.R"
    left_ear: str = "cgt_ear.L"
    right_ear: str = "cgt_ear.R"
    mouth_left: str = "cgt_left.L"
    mouth_right: str = "cgt_mouth.R"
    left_shoulder: str = "cgt_shoulder.L"
    right_shoulder: str = "cgt_shoulder.R"
    left_elbow: str = "cgt_elbow.L"
    right_elbow: str = "cgt_elbow.R"
    left_wrist: str = "cgt_pose_wrist.L"
    right_wrist: str = "cgt_pose_wrist.R"
    left_pinky: str = "cgt_pinky.L"
    right_pinky: str = "cgt_pinky.R"
    left_index: str = "cgt_index.L"
    right_index: str = "cgt_index.R"
    left_thumb: str = "cgt_thumb.L"
    right_thumb: str = "cgt_thumb.R"
    left_hip: str = "cgt_hip.L"
    right_hip: str = "cgt_hip.R"
    left_knee: str = "cgt_knee.L"
    right_knee: str = "cgt_knee.R"
    left_ankle: str = "cgt_ankle.L"
    right_ankle: str = "cgt_ankle.R"
    left_heel: str = "cgt_heel.L"
    right_heel: str = "cgt_heel.R"
    left_foot_index: str = "cgt_foot_index.L"
    right_foot_index: str = "cgt_foot_index.R"

    hip_center: str = "cgt_hip_center"
    shoulder_center: str = "cgt_shoulder_center"

    shoulder_center_ik: str = "cgt_shoulder_center_driver"
    left_shoulder_ik: str = "cgt_shoulder_driver.L"
    right_shoulder_ik: str = "cgt_shoulder_driver.R"
    left_forearm_ik: str = "cgt_forearm_driver.L"
    right_forearm_ik: str = "cgt_forearm_driver.R"
    left_hand_ik: str = "cgt_hand_driver.L"
    right_hand_ik: str = "cgt_hand_driver.R"
    left_index_ik: str = "cgt_index_driver.L"
    right_index_ik: str = "cgt_index_driver.R"

    hip_center_ik: str = "cgt_hip_center_driver"
    left_hip_ik: str = "cgt_hip_driver.L"
    right_hip_ik: str = "cgt_hip_driver.R"
    left_shin_ik: str = "cgt_shin_driver.L"
    right_shin_ik: str = "cgt_shin_driver.R"
    left_foot_ik: str = "cgt_foot_driver.L"
    right_foot_ik: str = "cgt_foot_driver.R"
    left_foot_index_ik: str = "cgt_foot_index_driver.L"
    right_foot_index_ik: str = "cgt_foot_index_driver.R"


@dataclass(frozen=True, init=False)
class HAND:
    wrist: str = "cgt_wrist"
    thumb_cmc: str = "cgt_thumb_cmc"
    thumb_mcp: str = "cgt_thumb_mcp"
    thumb_ip: str = "cgt_thump_ip"
    thumb_tip: str = "cgt_thumb_tip"
    index_finger_mcp: str = "cgt_index_mcp"
    index_finger_pip: str = "cgt_index_pip"
    index_finger_dip: str = "cgt_index_dip"
    index_finger_tip: str = "cgt_index_tip"
    middle_finger_mcp: str = "cgt_middle_mcp"
    middle_finger_pip: str = "cgt_middle_pip"
    middle_finger_dip: str = "cgt_middle_dip"
    middle_finger_tip: str = "cgt_middle_tip"
    ring_finger_mcp: str = "cgt_ring_mcp"
    ring_finger_pip: str = "cgt_ring_pip"
    ring_finger_dip: str = "cgt_ring_dip"
    ring_finger_tip: str = "cgt_ring_tip"
    pinky_mcp: str = "cgt_pinky_mcp"
    pinky_pip: str = "cgt_pinky_pip"
    pinky_dip: str = "cgt_pinky_dip"
    pinky_tip: str = "cgt_pinky_tip"

    driver_thumb_cmc: str = "cgt_thumb_cmc_driver"
    driver_thumb_mcp: str = "cgt_thumb_mcp_driver"
    driver_thumb_ip: str = "cgt_thump_ip_driver"
    driver_thumb_tip: str = "cgt_thumb_tip_driver"
    driver_index_finger_mcp: str = "cgt_index_mcp_driver"
    driver_index_finger_pip: str = "cgt_index_pip_driver"
    driver_index_finger_dip: str = "cgt_index_dip_driver"
    driver_index_finger_tip: str = "cgt_index_tip_driver"
    driver_middle_finger_mcp: str = "cgt_middle_mcp_driver"
    driver_middle_finger_pip: str = "cgt_middle_pip_driver"
    driver_middle_finger_dip: str = "cgt_middle_dip_driver"
    driver_middle_finger_tip: str = "cgt_middle_tip_driver"
    driver_ring_finger_mcp: str = "cgt_ring_mcp_driver"
    driver_ring_finger_pip: str = "cgt_ring_pip_driver"
    driver_ring_finger_dip: str = "cgt_ring_dip_driver"
    driver_ring_finger_tip: str = "cgt_ring_tip_driver"
    driver_pinky_mcp: str = "cgt_pinky_mcp_driver"
    driver_pinky_pip: str = "cgt_pinky_pip_driver"
    driver_pinky_dip: str = "cgt_pinky_dip_driver"
    driver_pinky_tip: str = "cgt_pinky_tip_driver"


@dataclass(frozen=True, init=False)
class FACE:
    face: str = "cgt_face_vertex_"

    head: str = "cgt_face_rotation"
    chin: str = "cgt_chin_rotation"
    mouth: str = "cgt_mouth_driver"
    mouth_corners: str = "cgt_mouth_corner_driver"
    left_eye: str = "cgt_eye_driver.L"
    right_eye: str = "cgt_eye_driver.R"
    right_eyebrow: str = "cgt_eyebrow_driver.R"
    left_eyebrow: str = "cgt_eyebrow_driver.L"

    right_eye_t: str = "cgt_eye_driver.T.R"
    right_eye_b: str = "cgt_eye_driver.B.R"
    left_eye_t: str = "cgt_eye_driver.T.L"
    left_eye_b: str = "cgt_eye_driver.B.L"
    mouth_t: str = "cgt_mouth_driver.T"
    mouth_b: str = "cgt_mouth_driver.B"
    mouth_r: str = "cgt_mouth_driver.R"
    mouth_l: str = "cgt_mouth_driver.L"

    eyebrow_in_l: str = "cgt_eyebrow.I.L"
    eyebrow_mid_l: str = "cgt_eyebrow.M.L"
    eyebrow_out_l: str = "cgt_eyebrow.O.L"

    eyebrow_in_r: str = "cgt_eyebrow.I.R"
    eyebrow_mid_r: str = "cgt_eyebrow.M.R"
    eyebrow_out_r: str = "cgt_eyebrow.O.R"
