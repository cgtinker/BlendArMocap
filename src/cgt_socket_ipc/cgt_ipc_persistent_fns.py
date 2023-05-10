from typing import Optional
from ..cgt_core.cgt_core_chains import (
    FaceNodeChain, PoseNodeChain, HandNodeChain, HolisticNodeChainGroup
)
from .BlendPyNet.b3dnet.src.b3dnet.connection import CACHE


# dict slots for mediapipe result processing
POSE_CHAIN_ID = "_CGT_LOCAL_CHAIN_POSE"
FACE_CHAIN_ID = "_CGT_LOCAL_CHAIN_FACE"
HOLI_CHAIN_ID = "_CGT_LOCAL_CHAIN_HOLISTIC"
HAND_CHAIN_ID = "_CGT_LOCAL_CHAIN_HAND"

# persistent fns which only get removed when activly
# CLEAR_CACHE gets called
POSE_FN_ID = "PERSISTENT_FN_POSE"
FACE_FN_ID = "PERSISTENT_FN_FACE"
HAND_FN_ID = "PERSISTENT_FN_HAND"
HOLI_FN_ID = "PERSISTENT_FN_HOLISTIC"


def process_holisitic(data: Optional[list], frame: int):
    # Input -> data: List[List[pose], List[face], List[l_hand], List[r_hand]], int
    if not data:
        return False

    if CACHE.get(HOLI_CHAIN_ID) is None:
        CACHE[HOLI_CHAIN_ID] = HolisticNodeChainGroup()

    data = [[[i, p] for i, p in enumerate(model)] for model in data]
    pose, face, lhand, rhand = data
    hands = [[lhand], [rhand]]
    CACHE[HOLI_CHAIN_ID].update([hands, [face], pose], frame)
    return True


def process_pose(data: Optional[list], frame: int):
    # Input: List[List[float, float, float]], int
    if not data:
        return False

    if CACHE.get(POSE_CHAIN_ID) is None:
        CACHE[POSE_CHAIN_ID] = PoseNodeChain()

    data = [[i, p] for i, p in enumerate(data)]
    CACHE[POSE_CHAIN_ID].update(data, frame)
    return True


def process_hand(data: Optional[list], frame: int):
    # Input: List[List[float, float, float], List[float, float, float]], int
    if not data:
        return False

    if CACHE.get(HAND_CHAIN_ID) is None:
        CACHE[HAND_CHAIN_ID] = HandNodeChain()

    data = [[[[i, p] for i, p in enumerate(hand)]] for hand in data]
    CACHE[HAND_CHAIN_ID].update(data, frame)
    return True


def process_face(data: Optional[list], frame: int):
    # Input: List[List[float, float, float]], int
    if not data:
        return False

    if CACHE.get(FACE_CHAIN_ID) is None:
        CACHE[FACE_CHAIN_ID] = FaceNodeChain()

    data = [[i, p] for i, p in enumerate(data)]
    CACHE[FACE_CHAIN_ID].update([data], frame)
    return True
