from abc import ABC, abstractmethod


class BridgeModel(ABC):
    @abstractmethod
    def initialize_bridge(self):
        pass

    @abstractmethod
    def initialize_model(self):
        pass

    @abstractmethod
    def process_detection_result(self, mp_res):
        pass

    @abstractmethod
    def contains_features(self, mp_res):
        pass

    @abstractmethod
    def draw_result(self, s, mp_res, mp_drawings, mp_hands):
        pass


