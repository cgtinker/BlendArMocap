import importlib

import m_CONST
from _blender.rig import abs_rigging
from _blender.utils import objects
from utils import log

importlib.reload(log)
importlib.reload(abs_rigging)
importlib.reload(objects)
importlib.reload(m_CONST)


class RigifyHands(abs_rigging.BpyRigging):
    def __init__(self, armature, driver_objects):
        # driver to rigify rig transfer name references
        self.references = {
            m_CONST.HAND.wrist.value: "hand_ik",
            m_CONST.HAND.thumb_cmc.value: "thumb.01",
            m_CONST.HAND.thumb_mcp.value: "thumb.02",
            m_CONST.HAND.thumb_ip.value: "thumb.03",
            m_CONST.HAND.thumb_tip.value: "thumb.01",
            m_CONST.HAND.index_finger_mcp.value: "f_index.01",
            m_CONST.HAND.index_finger_pip.value: "f_index.02",
            m_CONST.HAND.index_finger_dip.value: "f_index.03",
            m_CONST.HAND.index_finger_tip.value: "f_index.01",
            m_CONST.HAND.middle_finger_mcp.value: "f_middle.01",
            m_CONST.HAND.middle_finger_pip.value: "f_middle.02",
            m_CONST.HAND.middle_finger_dip.value: "f_middle.03",
            m_CONST.HAND.middle_finger_tip.value: "f_middle.01",
            m_CONST.HAND.ring_finger_mcp.value: "f_ring.01",
            m_CONST.HAND.ring_finger_pip.value: "f_ring.02",
            m_CONST.HAND.ring_finger_dip.value: "f_ring.03",
            m_CONST.HAND.ring_finger_tip.value: "f_ring.01",
            m_CONST.HAND.pinky_mcp.value: "f_pinky.01",
            m_CONST.HAND.pinky_pip.value: "f_pinky.02",
            m_CONST.HAND.pinky_dip.value: "f_pinky.03",
            m_CONST.HAND.pinky_tip.value: "f_pinky.01",
        }

        # storing relations between rigify and driver rig (left / right hand)
        self.relation_dict = {}
        self.set_relation_dict(driver_objects)
        self.apply_drivers(armature)

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
                log.logger.Error("Driver empty does not exist: ", empty.name)

    def apply_drivers(self, armature):
        # hand angles just require rotation m_CONSTraints for remapping
        pose_bones = armature.pose.bones
        for key, value in self.relation_dict.items():
            self.add_constraint(pose_bones[key], value, 'COPY_ROTATION')
