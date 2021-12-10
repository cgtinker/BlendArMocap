from blender import objects
from bridge.receiver.abstract_receiver import DataAssignment
from utils import log


class Pose(DataAssignment):
    def __init__(self):
        self.references = {
            0: "nose",
            1: "left_eye_inner",
            2: "left_eye",
            3: "right_eye_outer",
            4: "right_eye_inner",
            5: "right_eye",
            6: "right_eye_outer",
            7: "left_ear",
            8: "right_ear",
            9: "mouth_left",
            10: "mouth_right",
            11: "left_shoulder",
            12: "right_shoulder",
            13: "left_elbow",
            14: "right_elbow",
            15: "left_wrist",
            16: "right_wrist",
            17: "left_pinky",
            18: "right_pinky",
            19: "left_index",
            20: "right_index",
            21: "left_thumb",
            22: "right_thumb",
            23: "left_hip",
            24: "right_hip",
            25: "left_knee",
            26: "right_knee",
            27: "left_ankle",
            28: "right_ankle",
            29: "left_heel",
            30: "right_heel",
            31: "left_foot_index",
            32: "right_foot_index"

        }
        self.pose = []

    def init_references(self):
        self.pose = objects.generate_empties(self.references, 0.1)

    def set_position(self, frame):
        pass

    def set_position_b(self, frame):
        """Keyframe the position of input data."""
        try:
            print(self.data, frame)
        except IndexError:
            log.logger.error("VALUE ERROR WHILE ASSIGNING HAND POSITION")

    def allocate_memory_b(self, idx, data):
        """Store Detection data in memory."""
        d = list(zip(data[0], data[1]))
        self.memory_stack[f'{idx}'] = d