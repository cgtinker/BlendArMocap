from ...cgt_naming import HAND
from . import abs_rigging


class RigifyHands(abs_rigging.BpyRigging):
    def __init__(self, armature, driver_objects):
        # driver to rigify cgt_rig transfer name references
        self.references = {
            HAND.wrist:             "hand_ik",
            HAND.thumb_cmc:         "thumb.01",
            HAND.thumb_mcp:         "thumb.02",
            HAND.thumb_ip:          "thumb.03",
            HAND.thumb_tip:         "thumb.01",
            HAND.index_finger_mcp:  "f_index.01",
            HAND.index_finger_pip:  "f_index.02",
            HAND.index_finger_dip:  "f_index.03",
            HAND.index_finger_tip:  "f_index.01",
            HAND.middle_finger_mcp: "f_middle.01",
            HAND.middle_finger_pip: "f_middle.02",
            HAND.middle_finger_dip: "f_middle.03",
            HAND.middle_finger_tip: "f_middle.01",
            HAND.ring_finger_mcp:   "f_ring.01",
            HAND.ring_finger_pip:   "f_ring.02",
            HAND.ring_finger_dip:   "f_ring.03",
            HAND.ring_finger_tip:   "f_ring.01",
            HAND.pinky_mcp:         "f_pinky.01",
            HAND.pinky_pip:         "f_pinky.02",
            HAND.pinky_dip:         "f_pinky.03",
            HAND.pinky_tip:         "f_pinky.01",
        }

        # storing relations between rigify and driver cgt_rig (left / right hand)
        self.relation_dict = {}
        self.set_relation_dict(driver_objects)
        self.m_apply_drivers(armature)

    def get_reference_bone(self, key, extension):
        """ get reference bone by driver empty name. """
        if "TIP" in key:
            # rigify finger tip has .001 extension (why ever..)
            bone_name = self.references[key] + extension + ".001"
            return bone_name

        bone_name = self.references[key] + extension
        return bone_name

    def set_relation_dict(self, driver_empties):
        """ sets relation dict containing bone name and reference empty obj. """
        for empty in driver_empties:
            # can be left / right hand
            if ".L" in empty.name:
                extension = ".L"
            else:
                extension = ".R"

            # remove extension from driver name
            name = empty.name.replace(extension, "")
            try:
                bone_name = self.get_reference_bone(name, extension)
                self.relation_dict[bone_name] = empty

            except KeyError:
                print("driver empty does not exist:", empty.name)

    def m_apply_drivers(self, armature):
        # hand angles just require rotation m_CONSTraints for remapping
        pose_bones = armature.pose.bones
        for key, value in self.relation_dict.items():
            self.add_constraint(pose_bones[key], value, 'COPY_ROTATION')
