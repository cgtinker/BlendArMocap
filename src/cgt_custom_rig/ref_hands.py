from . import RigReference
from .. import cgt_naming


class RigHands(RigReference.BoneNameProvider):
    name = "hands"
    rigify_bone_refs = {
        cgt_naming.HAND.wrist + ".R":             "hand_ik.R",
        cgt_naming.HAND.thumb_cmc + ".R":         "thumb.01.R",
        cgt_naming.HAND.thumb_mcp + ".R":         "thumb.02.R",
        cgt_naming.HAND.thumb_ip + ".R":          "thumb.03.R",
        cgt_naming.HAND.thumb_tip + ".R":         "thumb.01.R.001",
        cgt_naming.HAND.index_finger_mcp + ".R":  "f_index.01.R",
        cgt_naming.HAND.index_finger_pip + ".R":  "f_index.02.R",
        cgt_naming.HAND.index_finger_dip + ".R":  "f_index.03.R",
        cgt_naming.HAND.index_finger_tip + ".R":  "f_index.01.R.001",
        cgt_naming.HAND.middle_finger_mcp + ".R": "f_middle.01.R",
        cgt_naming.HAND.middle_finger_pip + ".R": "f_middle.02.R",
        cgt_naming.HAND.middle_finger_dip + ".R": "f_middle.03.R",
        cgt_naming.HAND.middle_finger_tip + ".R": "f_middle.01.R.001",
        cgt_naming.HAND.ring_finger_mcp + ".R":   "f_ring.01.R",
        cgt_naming.HAND.ring_finger_pip + ".R":   "f_ring.02.R",
        cgt_naming.HAND.ring_finger_dip + ".R":   "f_ring.03.R",
        cgt_naming.HAND.ring_finger_tip + ".R":   "f_ring.01.R.001",
        cgt_naming.HAND.pinky_mcp + ".R":         "f_pinky.01.R",
        cgt_naming.HAND.pinky_pip + ".R":         "f_pinky.02.R",
        cgt_naming.HAND.pinky_dip + ".R":         "f_pinky.03.R",
        cgt_naming.HAND.pinky_tip + ".R":         "f_pinky.01.R.001",

        cgt_naming.HAND.wrist + ".L":              "hand_ik.L",
        cgt_naming.HAND.thumb_cmc + ".L":          "thumb.01.L",
        cgt_naming.HAND.thumb_mcp + ".L":          "thumb.02.L",
        cgt_naming.HAND.thumb_ip + ".L":           "thumb.03.L",
        cgt_naming.HAND.thumb_tip + ".L":          "thumb.01.L.001",
        cgt_naming.HAND.index_finger_mcp + ".L":   "f_index.01.L",
        cgt_naming.HAND.index_finger_pip + ".L":   "f_index.02.L",
        cgt_naming.HAND.index_finger_dip + ".L":   "f_index.03.L",
        cgt_naming.HAND.index_finger_tip + ".L":   "f_index.01.L.001",
        cgt_naming.HAND.middle_finger_mcp + ".L":  "f_middle.01.L",
        cgt_naming.HAND.middle_finger_pip + ".L":  "f_middle.02.L",
        cgt_naming.HAND.middle_finger_dip + ".L":  "f_middle.03.L",
        cgt_naming.HAND.middle_finger_tip + ".L":  "f_middle.01.L.001",
        cgt_naming.HAND.ring_finger_mcp + ".L":    "f_ring.01.L",
        cgt_naming.HAND.ring_finger_pip + ".L":    "f_ring.02.L",
        cgt_naming.HAND.ring_finger_dip + ".L":    "f_ring.03.L",
        cgt_naming.HAND.ring_finger_tip + ".L":    "f_ring.01.L.001",
        cgt_naming.HAND.pinky_mcp + ".L":          "f_pinky.01.L",
        cgt_naming.HAND.pinky_pip + ".L":          "f_pinky.02.L",
        cgt_naming.HAND.pinky_dip + ".L":          "f_pinky.03.L",
        cgt_naming.HAND.pinky_tip + ".L":          "f_pinky.01.L.001",
    }

    def provide_bone_names(self):
        return self.rigify_bone_refs


def main():
    hands = RigHands()
    refs = hands.provide_bone_names()
    hands.to_json(refs, "hands")


if __name__ == '__main__':
    main()
