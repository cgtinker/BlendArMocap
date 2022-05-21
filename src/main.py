from .cgt_bridge import bpy_hand_bridge, bpy_pose_bridge, bpy_face_bridge, bpy_bridge_interface, print_bridge
from .cgt_detection import detect_hands, detect_pose, detect_face, detect_holistic, detector_interface
from .cgt_patterns import events
from .cgt_processing import hand_processing, pose_processing, face_processing, processor_interface
from .cgt_utils import stream


class DetectionHandler:
    target: str = ""
    detector: detector_interface = None
    bridge: bpy_bridge_interface = None
    processor: processor_interface = None

    # bridge to assign to blender
    bpy_bridges = {
        "HAND":     bpy_hand_bridge.BpyHandBridge,
        "POSE":     bpy_pose_bridge.BpyPoseBridge,
        "FACE":     bpy_face_bridge.BpyFaceBridge,
        "HOLISTIC": [bpy_hand_bridge.BpyHandBridge, bpy_pose_bridge.BpyPoseBridge, bpy_face_bridge.BpyFaceBridge]
    }

    # bridge for printing
    print_bridges = {
        "HAND": print_bridge.PrintBridge,
        "POSE": print_bridge.PrintBridge,
        "FACE": print_bridge.PrintBridge,
        "HOLISTIC": [print_bridge.PrintBridge]*3
    }

    # detection types and processors
    detection_types = {
        "HAND":     detect_hands.HandDetector,
        "POSE":     detect_pose.PoseDetector,
        "FACE":     detect_face.FaceDetector,
        "HOLISTIC": detect_holistic.HolisticDetector
    }

    # processes mediapipe landmarks
    processor_types = {
        "HAND": hand_processing.HandProcessor,
        "POSE": pose_processing.PoseProcessor,
        "FACE": face_processing.FaceProcessor,
        "HOLISTIC": [hand_processing.HandProcessor, pose_processing.PoseProcessor, face_processing.FaceProcessor]
    }

    # observes data and maps it to the bridge
    observers = {
        "BPY":             events.BpyUpdateReceiver,
        "PRINT_RAW":       events.PrintRawDataUpdate,
        "PRINT_PROCESSED": events.DriverDebug   # may doesn't while working with mathutils
    }

    def __init__(self, target: str = "HAND", bridge_type: str = "BPY"):
        """ Initialize a detection handler using a detection target type and a bridge type.
            A mediapipe model handles the detection in a cv2 stream. The data is getting processed
            for blender. It's also possible to print data using the print bridges. """
        self.detector: detector_interface.RealtimeDetector = self.detection_types[target]
        self.processor: processor_interface.DataProcessor = self.processor_types[target]

        bridge_types = {
            "BPY":             self.bpy_bridges,
            "PRINT_PROCESSED": self.print_bridges,
            "PRINT_RAW":       self.print_bridges
        }

        # assign or print data (processed printing only available for location and scale data)
        self.bridge = bridge_types[bridge_type][target]

        # observers input and feeds processor with detection results
        self.listener = events.UpdateListener()
        self.observer = self.observers[bridge_type]

    def init_detector(self, capture_input=None, dimension: str = "sd", backend: int = 0,
                      frame_start: int = 0, key_step: int = 1, input_type: str = "movie"):
        """ Init stream and detector using preselected detection type.
            :param capture_input: cap input for cv2 (b.e. int or filepath)
            :param dimension: dimensions of the cv2 stream ["sd", "hd", "fhd"]
            :param backend: default or capdshow [0, 1]
            :param frame_start: key frame start in blender timeline
            :param key_step: keyframe step for capture results
            :param input_type: "movie" or "stream" input
            :return: returns nothing: """
        # initialize the detector
        self.detector = self.detector(frame_start=frame_start, key_step=key_step, input_type=input_type)

        # stream capture dimensions
        dimensions_dict = {
            "sd":  [720, 480],
            "hd":  [1240, 720],
            "fhd": [1920, 1080]
        }
        dim = dimensions_dict[dimension]

        # default webcam slot
        if capture_input is None:
            capture_input = 0

        # init tracking handler targets
        self.detector.stream = stream.Webcam(
            capture_input=capture_input, width=dim[0], height=dim[1], backend=backend
        )

        # stop if opening stream failed
        if not self.detector.stream.capture.isOpened():
            raise IOError("Initializing Detector failed.")

        # initialize mediapipe model
        self.detector.initialize_model()

    def init_bridge(self):
        """ Initialize bridge to print raw data / to blender. """
        if self.observer == events.PrintRawDataUpdate:
            self.processor = None

        # initialize bridge to blender / printing
        self.detector.init_bridge(
            processor=self.processor,
            bridge=self.bridge,
            observer=self.observer,
            listener=self.listener
        )

    def __del__(self):
        del self.detector


def main():
    handler = DetectionHandler("FACE", "PRINT_RAW")
    handler.init_detector(0, "sd", 0, 0, 0, "stream")
    handler.init_bridge()

    for _ in range(20):
        handler.detector.image_detection()

    del handler


if __name__ == '__main__':
    main()
