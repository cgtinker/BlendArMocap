from blender import objects
from bridge.receiver import abstract_receiver
from utils import log, vector_math
from mathutils import Vector
import importlib

importlib.reload(abstract_receiver)


class Pose(abstract_receiver.DataAssignment):
    def __init__(self):
        self.references = {
            0: "nose",
            1: "left_eye_inner",
            2: "left_eye",
            3: "left_eye_outer",
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
        self.init_references()
        self.col_name = "Pose"

    def init_references(self):
        # default empties
        self.pose = objects.add_empties(self.references, 0.025)

        # custom mapping references
        self.pose.append(objects.add_empty(size=0.025, name="shoulder_center"))
        self.pose.append(objects.add_empty(size=0.025, name="hip_center"))
        self.pose.append(objects.add_empty(size=0.05, name="origin"))

        objects.set_parents(self.pose[len(self.pose)], self.pose[:len(self.pose)-1])
        objects.add_list_to_collection(self.col_name, self.pose)

    def set_position(self, frame):
        """Keyframe the position of input data."""
        self.append_custom_data()

        try:
            self.translate(self.pose, self.data, frame)

        except IndexError:
            log.logger.error("VALUE ERROR WHILE ASSIGNING POSE POSITION")

        self.set_custom_rotation(frame)

    def set_custom_rotation(self, frame):
        a, b = self.get_vector_by_entry(11), self.get_vector_by_entry(12)
        shoulder_rot = vector_math.rotate_towards(Vector((-a[0], a[2], -a[1])), Vector((-b[0], b[2], -b[1])))

        a, b = self.get_vector_by_entry(23), self.get_vector_by_entry(24)
        hip_rot = vector_math.rotate_towards(Vector((-a[0], a[2], -a[1])), Vector((-b[0], b[2], -b[1])))

        data = [
            [33, [shoulder_rot[0], shoulder_rot[1], shoulder_rot[2]]],
            [34, [hip_rot[0], hip_rot[1], hip_rot[2]]]
        ]

        print("DATA:", data)
        self.euler_rotate(self.pose, data, frame)

    def append_custom_data(self):
        """ appending custom rotation data to native ml array. """
        shoulder_cp = vector_math.get_center_point(self.get_vector_by_entry(11), self.get_vector_by_entry(12))
        self.data.append([33, [shoulder_cp[0], shoulder_cp[1], shoulder_cp[2]]])

        hip_cp = vector_math.get_center_point(self.get_vector_by_entry(23), self.get_vector_by_entry(24))
        self.data.append([34, [hip_cp[0], hip_cp[1], hip_cp[2]]])

    def allocate_memory_b(self, idx, data):
        """Store Detection data in memory."""
        self.memory_stack[f'{idx}'] = data
