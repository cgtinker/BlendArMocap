from utils import log
from blender import abs_rigging, objects
import importlib

importlib.reload(abs_rigging)
importlib.reload(objects)


class RigifyHands(abs_rigging.BpyRigging):
    def __init__(self, armature, driver_objects):
        self.references = {
            "cgt_WRIST":                "hand_fk",
            "cgt_THUMB_CMC":            "thumb.01",
            "cgt_THUMB_MCP":            "thumb.02",
            "cgt_THUMP_IP":             "thumb.03",
            "cgt_THUMB_TIP":            "thumb.01",
            "cgt_INDEX_FINGER_MCP":     "f_index.01",
            "cgt_INDEX_FINGER_PIP":     "f_index.02",
            "cgt_INDEX_FINGER_DIP":     "f_index.03",
            "cgt_INDEX_FINGER_TIP":     "f_index.01",
            "cgt_MIDDLE_FINGER_MCP":    "f_middle.01",
            "cgt_MIDDLE_FINGER_PIP":    "f_middle.02",
            "cgt_MIDDLE_FINGER_DIP":    "f_middle.03",
            "cgt_MIDDLE_FINGER_TIP":    "f_middle.01",
            "cgt_RING_FINGER_MCP":      "f_ring.01",
            "cgt_RING_FINGER_PIP":      "f_ring.02",
            "cgt_RING_FINGER_DIP":      "f_ring.03",
            "cgt_RING_FINGER_TIP":      "f_ring.01",
            "cgt_PINKY_MCP":            "f_pinky.01",
            "cgt_PINKY_PIP":            "f_pinky.02",
            "cgt_PINKY_DIP":            "f_pinky.03",
            "cgt_PINKY_TIP":            "f_pinky.01",
        }

        self.relation_dict = {}
        self.extension = ""

        self.set_relation_dict(driver_objects)
        self.apply_drivers(armature)

    def get_reference_bone(self, key):
        """ get reference bone by driver empty name. """
        if "TIP" in key:
            bone_name = self.references[key] + self.extension + ".001"
            return bone_name

        bone_name = self.references[key] + self.extension
        return bone_name

    def set_relation_dict(self, driver_empties):
        """ sets relation dict containing bone name and reference empty obj. """
        for empty in driver_empties:
            if ".L" in empty.name:
                self.extension = ".L"
            else:
                self.extension = ".R"

            # remove extension from driver name
            name = empty.name.replace(self.extension, "")
            try:
                bone_name = self.get_reference_bone(name)
                self.relation_dict[bone_name] = empty

            except KeyError:
                print("driver empty does not exist:", empty.name)
                # log.logger.Error("Driver empty does not exist: ", empty.name)

    def apply_drivers(self, armature):
        bones = objects.get_armature_bones(armature)
        pose_bones = armature.pose.bones
        for key, value in self.relation_dict.items():
            self.add_constraint(pose_bones[key], value, 4)
