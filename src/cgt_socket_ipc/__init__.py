from .BlendPyNet.b3dnet.src.b3dnet.connection import CACHE
from . import cgt_ipc_persistent_fns as fns


init_fns = [
    (fns.process_holisitic, fns.HOLI_FN_ID),
    (fns.process_face, fns.FACE_FN_ID),
    (fns.process_hand, fns.HAND_FN_ID),
    (fns.process_pose, fns.POSE_FN_ID)
]

for _fn, _id in init_fns:
    CACHE[_id] = _fn
