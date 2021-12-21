from blender import objects
from bridge.receiver import abstract_receiver
import importlib

importlib.reload(objects)
importlib.reload(abstract_receiver)


class BridgeHand(abstract_receiver.DataAssignment):
    def __init__(self, mode='realtime'):
        self.references = {
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
        self.col_name = "Hands"

        if mode == 'realtime':
            self.init_references()

    def init_references(self):
        """Generate empty objects."""
        self.left_hand = objects.add_empties(self.references, 0.005, ".L")
        self.right_hand = objects.add_empties(self.references, 0.005, ".R")
        
        parent_l = objects.add_empty(0.025, "Hand.L")
        parent_r = objects.add_empty(0.025, "Hand.R")
        objects.set_parents(parent_l, self.left_hand)
        objects.set_parents(parent_r, self.right_hand)
        self.left_hand.append(parent_l)
        self.right_hand.append(parent_r)

        objects.add_list_to_collection(self.col_name, self.left_hand)
        objects.add_list_to_collection(self.col_name, self.right_hand)

    def set_position(self, frame):
        """Keyframe the position of input data."""
        left_positions, right_positions = self.assign_hands(list(zip(self.data[0], self.data[1])))
        self.try_translating(self.left_hand, left_positions, frame)
        self.try_translating(self.right_hand, right_positions, frame)

    def try_translating(self, hand, positions, frame):
        try:
            self.translate(hand, positions[0], frame)
        except IndexError:
            pass

    def set_custom_rotation(self, frame):
        pass

    def allocate_memory(self, idx, data):
        """Store Detection data in memory."""
        d = list(zip(data[0], data[1]))
        self.memory_stack[f'{idx}'] = d

    @staticmethod
    def assign_hands(hand_data):
        """Determines where the data belongs to"""
        left_hand = [data[0] for data in hand_data if data[1][1] is True]
        right_hand = [data[0] for data in hand_data if data[1][1] is False]
        return left_hand, right_hand
