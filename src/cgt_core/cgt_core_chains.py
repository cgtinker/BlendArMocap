from __future__ import annotations
from typing import List

from .cgt_calculators_nodes import mp_calc_face_rot, mp_calc_pose_rot, mp_calc_hand_rot
from .cgt_output_nodes import mp_hand_out, mp_face_out, mp_pose_out
from .cgt_patterns import cgt_nodes


class FaceNodeChain(cgt_nodes.NodeChain):
    def __init__(self):
        super().__init__()
        self.append(mp_calc_face_rot.FaceRotationCalculator())
        self.append(mp_face_out.MPFaceOutputNode())


class PoseNodeChain(cgt_nodes.NodeChain):
    def __init__(self):
        super().__init__()
        self.append(mp_calc_pose_rot.PoseRotationCalculator())
        self.append(mp_pose_out.MPPoseOutputNode())


class HandNodeChain(cgt_nodes.NodeChain):
    def __init__(self):
        super().__init__()
        self.append(mp_calc_hand_rot.HandRotationCalculator())
        self.append(mp_hand_out.CgtMPHandOutNode())


class HolisticNodeChainGroup(cgt_nodes.NodeChainGroup):
    nodes: List[cgt_nodes.NodeChain]

    def __init__(self):
        super().__init__()
        self.nodes.append(HandNodeChain())
        self.nodes.append(FaceNodeChain())
        self.nodes.append(PoseNodeChain())

