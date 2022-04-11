from . import RigReference
from .. import cgt_naming
import json


class RigHands(RigReference.BoneNameProvider):
    rigify_bone_refs = {
        "wrist.R":             "hand_ik.R",
        "thumb_cmc.R":         "thumb.01.R",
        "thumb_mcp.R":         "thumb.02.R",
        "thumb_ip.R":          "thumb.03.R",
        "thumb_tip.R":         "thumb.01.R.001",
        "index_finger_mcp.R":  "f_index.01.R",
        "index_finger_pip.R":  "f_index.02.R",
        "index_finger_dip.R":  "f_index.03.R",
        "index_finger_tip.R":  "f_index.01.R.001",
        "middle_finger_mcp.R": "f_middle.01.R",
        "middle_finger_pip.R": "f_middle.02.R",
        "middle_finger_dip.R": "f_middle.03.R",
        "middle_finger_tip.R": "f_middle.01.R.001",
        "ring_finger_mcp.R":   "f_ring.01.R",
        "ring_finger_pip.R":   "f_ring.02.R",
        "ring_finger_dip.R":   "f_ring.03.R",
        "ring_finger_tip.R":   "f_ring.01.R.001",
        "pinky_mcp.R":         "f_pinky.01.R",
        "pinky_pip.R":         "f_pinky.02.R",
        "pinky_dip.R":         "f_pinky.03.R",
        "pinky_tip.R":         "f_pinky.01.R.001",

        "wrist.L":             "hand_ik.L",
        "thumb_cmc.L":         "thumb.01.L",
        "thumb_mcp.L":         "thumb.02.L",
        "thumb_ip.L":          "thumb.03.L",
        "thumb_tip.L":         "thumb.01.L.001",
        "index_finger_mcp.L":  "f_index.01.L",
        "index_finger_pip.L":  "f_index.02.L",
        "index_finger_dip.L":  "f_index.03.L",
        "index_finger_tip.L":  "f_index.01.L.001",
        "middle_finger_mcp.L": "f_middle.01.L",
        "middle_finger_pip.L": "f_middle.02.L",
        "middle_finger_dip.L": "f_middle.03.L",
        "middle_finger_tip.L": "f_middle.01.L.001",
        "ring_finger_mcp.L":   "f_ring.01.L",
        "ring_finger_pip.L":   "f_ring.02.L",
        "ring_finger_dip.L":   "f_ring.03.L",
        "ring_finger_tip.L":   "f_ring.01.L.001",
        "pinky_mcp.L":         "f_pinky.01.L",
        "pinky_pip.L":         "f_pinky.02.L",
        "pinky_dip.L":         "f_pinky.03.L",
        "pinky_tip.L":         "f_pinky.01.L.001",
    }

    def provide_bone_names(self):
        return self.rigify_bone_refs

def main():
    hands = RigHands()
    refs = hands.provide_bone_names()
    hands.to_json(refs, "hands")


if __name__ == '__main__':
    main()
