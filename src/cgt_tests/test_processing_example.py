import unittest
from src.cgt_core.cgt_calculators import face_processing, hand_processing, pose_processing
from src.cgt_core.cgt_bridge import custom_data_container
from src.cgt_core.cgt_utils import cgt_json

""" This isn't a real test, it only will trigger location related errors.
    Has to be tested within blender or with blender build as Module.
    However, it delivers a good example on how to use Processors and how to create a Bridge. """


class TestBridge:
    target_type = None

    def __init__(self, *args):
        self.target_type = args[0]

    def get_instances(self):
        # this may doesn't match the requirements for every processor
        # display for shape, only custom data containers are required
        if self.target_type == "FACE":
            return [[], [custom_data_container.CustomData() for _ in range(0, 8)]]
        elif self.target_type == "HAND":
            return [], []
        elif self.target_type == "POSE":
            return [], custom_data_container.CustomData(), custom_data_container.CustomData()

    def set_position(self, data, frame):
        print(data, frame)
        pass

    def set_rotation(self, data, frame):
        print(data, frame)
        pass

    def set_scale(self, data, frame):
        print(data, frame)
        pass


class TestProcessing(unittest.TestCase):
    def test_face_processing(self):
        data = cgt_json.JsonData("data/face_data.json")
        data = data.data
        # init processor bridge
        face = face_processing.FaceRotationcalculator(TestBridge)
        face.init_references()

        # process data
        face.data = data
        face.init_print()
        face.update()

    def test_pose_processing(self):
        return
        data = cgt_json.from_json("data/face_data.json")

        # init processor bridge
        face = pose_processing.PoseRotationCalculator(TestBridge)
        face.init_references()

        # process data
        face.data = data
        face.init_print()
        face.update()

    def test_hand_processing(self):
        return
        data = cgt_json.from_json("data/face_data.json")

        # init processor bridge
        face = hand_processing.HandRotationCalculator(TestBridge)
        face.init_references()

        # process data
        face.data = data
        face.init_print()
        face.update()


if __name__ == '__main__':
    unittest.main()
