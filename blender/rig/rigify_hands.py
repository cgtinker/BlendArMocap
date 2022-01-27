# Copyright (C) cgtinker, cgtinker.com, hello@cgtinker.com
from blender.rig import abs_rigging
from blender.utils import objects
import importlib

importlib.reload(abs_rigging)
importlib.reload(objects)


class RigifyHands(abs_rigging.BpyRigging):
    def __init__(self, armature, driver_objects):
        # driver to rigify rig transfer name references
        self.references = {
            "cgt_WRIST":                "hand_ik",
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

        # storing relations between rigify and driver rig (left / right hand)
        self.relation_dict = {}
        self.set_relation_dict(driver_objects)
        # finally applying the drivers
        self.apply_drivers(armature)

    def get_reference_bone(self, key, extension):
        """ get reference bone by driver empty name. """
        if "TIP" in key:
            # rigify finger tip has .001 extension (whyever..)
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
                # log.logger.Error("Driver empty does not exist: ", empty.name)

    # hand angles just require rotation constraints for remapping
    def apply_drivers(self, armature):
        bones = objects.get_armature_bones(armature)
        pose_bones = armature.pose.bones
        for key, value in self.relation_dict.items():
            self.add_constraint(pose_bones[key], value, 'COPY_ROTATION')
