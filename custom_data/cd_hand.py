from blender import objects
from mathutils import Vector
import bpy


class Hand(object):
    def __init__(self):
        landmark_references = {
            0: "WRIST",
            1: "THUMB_CMC",
            2: "THUMB_MCP",
            3: "THUMP_IP",
            4: "THUMB_TIP",
            5: "INDEX_FINGER_MCP",
            6: "INDEX_FINGER_PIP",
            7: "INDEX_FINGER_DIP",
            8: "INDEX_FINGER_TIP",
            9: "MIDDLE_FINGER_MCP",
            10: "MIDDLE_FINGER_PIP",
            11: "MIDDLE_FINGER_DIP",
            12: "MIDDLE_FINGER_TIP",
            13: "RING_FINGER_MCP",
            14: "RING_FINGER_PIP",
            15: "RING_FINGER_DIP",
            16: "RING_FINGER_TIP",
            17: "PINKY_MCP",
            18: "PINKY_PIP",
            19: "PINKY_DIP",
            20: "PINKY_TIP"
        }

        self.objs = objects.generate_empties(landmark_references, 0.1)
        self.blender_link_handler()

    def set_position(self, data):
        for position_data in data[0]: # can be 2 hands
            for i, p in enumerate(position_data):
                self.objs[p[0]].location = Vector((p[1][0], p[1][1], p[1][2]))
        self.frame_change_pre()

    def blender_link_handler(self):
        bpy.app.handlers.frame_change_pre.append(self.frame_change_pre())

    def frame_change_pre(self):
        print("none")
        pass
