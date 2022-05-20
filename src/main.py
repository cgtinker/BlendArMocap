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
    }

    # bridge for printing
    print_bridges = {
        "HAND": print_bridge.PrintBridge,
        "POSE": print_bridge.PrintBridge,
        "FACE": print_bridge.PrintBridge,
    }

    # detection types and processors
    detection_types = {
        "HAND":     detect_hands.HandDetector,
        "POSE":     detect_pose.PoseDetector,
        "FACE":     detect_face.FaceDetector
    }

    # processes mediapipe landmarks
    processor_types = {
        "HAND": hand_processing.HandProcessor,
        "POSE": pose_processing.PoseProcessor,
        "FACE": face_processing.FaceProcessor,
    }

    # observes data and maps it to the bridge
    observers = {
        "BPY":             events.BpyUpdateReceiver,
        "PRINT_RAW":       events.PrintRawDataUpdate,
        "PRINT_PROCESSED": events.DriverDebug
    }

    def __init__(self, target: str = "HAND", bridge_type: str = "BPY"):
        """ Initialize a detection handler using a detection target type and a bridge type.
            A mediapipe model handles the detection in a cv2 stream. The data is getting processed
            by default for blender. It's also possible to print the processed data using the printer
            bridges. An observer pattern is in use to disconnect the detector from the processor. """
        self.detector: detector_interface.RealtimeDetector = self.detection_types[target]
        self.processor: processor_interface.DataProcessor = self.processor_types[target]

        bridge_types = {
            "BPY":             self.bpy_bridges,
            "PRINT_PROCESSED": self.print_bridges,
            "PRINT_RAW":       self.print_bridges
        }
        self.bridge = bridge_types[bridge_type][target]
        self.listener = events.UpdateListener
        self.observer = self.observers[bridge_type]

    def init_detector(self, capture_input=None, dimension: str = "sd", backend: int = 0,
                      frame_start: int = 0, key_step: int = 1, input_type: str = "movie"):
        """ Init stream and using selected detection type. """
        # intialize the detector
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

        # if opening stream failed
        if not self.detector.stream.capture.isOpened():
            raise IOError("Initializing Detector failed.")

    def init_bridge(self):
        # initialize mediapipe model
        self.detector.initialize_model()

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
    handler = DetectionHandler("FACE", "PRINT_PROCESSED")
    handler.init_detector(0, "sd", 0, 0, 0, "stream")
    handler.init_bridge()

    for _ in range(10):
        handler.detector.image_detection()

    del handler


if __name__ == '__main__':
    main()
