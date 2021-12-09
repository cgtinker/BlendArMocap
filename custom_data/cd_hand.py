from blender import objects
from mathutils import Vector
from utils.writer import json_writer
from utils import log


class Hand:
    def __init__(self, mode='realtime'):
        self.landmark_references = {
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

        self.left_hand = []
        self.right_hand = []

        self.data = None
        self.memory_stack = {}

        if mode == 'realtime':
            self.init_references()

    def init_references(self):
        """Generate empty objects."""
        self.left_hand = objects.generate_empties(self.landmark_references, 0.025, "_l")
        self.right_hand = objects.generate_empties(self.landmark_references, 0.025, "_r")

    def set_position(self, frame):
        """Keyframe the position of input data."""
        try:
            left_hand, right_hand = self.assign_hands(list(zip(self.data[0], self.data[1])))
            self.translate(self.left_hand, left_hand, frame)
            self.translate(self.right_hand, right_hand, frame)
        except IndexError:
            log.logger.error("VALUE ERROR WHILE ASSIGNING HAND POSITION")

    def translate(self, hand, data, frame):
        try:
            for p in data[0]:
                hand[p[0]].location = Vector((p[1][0], p[1][1], p[1][2]))
                hand[p[0]].keyframe_insert(data_path="location", frame=frame)

        except IndexError:
            pass

    def allocate_memory(self, idx, data):
        """Store Detection data in memory."""
        d = list(zip(data[0], data[1]))
        self.memory_stack[f'{idx}'] = d

    @staticmethod
    def assign_hands(hand_data):
        """Determines where the data belongs to"""
        """ removing switch to save preformance
        if len(hand_data) == 2:
            if hand_data[0][1][1] == hand_data[1][1][1]:
                return [], []
        """
        left_hand = [data[0] for data in hand_data if data[1][1] is True]
        right_hand = [data[0] for data in hand_data if data[1][1] is False]
        return left_hand, right_hand

    def write_json(self):
        """Writes a .json file for async processing"""
        writer = json_writer.JsonWriter('hand.json')
        writer.chunks = self.memory_stack
        writer.write()
