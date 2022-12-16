from __future__ import annotations
from typing import List

from .cgt_calculators_nodes import calc_face_rot_sca, calc_pose_rot_sca, calc_hand_rot
from .cgt_patterns import cgt_nodes


class FaceNodeChain(cgt_nodes.NodeChain):
    def __init__(self):
        super().__init__()
        self.append(calc_face_rot_sca.FaceRotationcalculator())


class PoseNodeChain(cgt_nodes.NodeChain):
    def __init__(self):
        super().__init__()
        self.append(calc_pose_rot_sca.PoseRotationCalculator())


class HandNodeChain(cgt_nodes.NodeChain):
    def __init__(self):
        super().__init__()
        self.append(calc_hand_rot.HandRotationCalculator())


class HolisticNodeChainGroup(cgt_nodes.NodeChainGroup):
    nodes: List[cgt_nodes.NodeChain]

    def __init__(self):
        super().__init__()
        self.nodes.append(HandNodeChain())
        self.nodes.append(FaceNodeChain())
        self.nodes.append(PoseNodeChain())
