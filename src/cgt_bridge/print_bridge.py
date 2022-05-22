from . import bridge_interface
from . import custom_data_container


class PrintBridge(bridge_interface.BridgeInterface):
    def __init__(self, target_type: str = "FACE"):
        print("PRINT BRIDGE GOT CALLED", target_type)
        self.target_type: str = target_type

    def get_instances(self):
        # this may doesn't match the requirements for every processor
        if self.target_type == "FACE":
            return [[], [custom_data_container.CustomData() for _ in range(0, 8)]]
        elif self.target_type == "HAND":
            return [], []
        elif self.target_type == "POSE":
            return [], custom_data_container.CustomData(), custom_data_container.CustomData()

    def set_position(self, data, frame):
        print(f"POSITION DATA at {frame}\n{data}")

    def set_rotation(self, data, frame):
        print(f"ROTATION DATA at {frame}\n{data}")

    def set_scale(self, data, frame):
        print(f"SCALE DATA at {frame}\n{data}")
