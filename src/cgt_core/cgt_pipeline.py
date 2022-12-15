from __future__ import annotations
from abc import ABC, abstractmethod
import numpy as np


class DataProvider(ABC):
    """ Provides input data of any shape. """
    @abstractmethod
    def get_data(self) -> (int, np.ndarray):
        """ Returns frame and data. """
        pass


class DataProcessor(ABC):
    """ Processes data by modifying shape, adding rotations and scale or changing locations. """
    @abstractmethod
    def set_data(self, data: np.ndarray) -> None:
        """ Push data to the processor. """
        pass

    @abstractmethod
    def get_data(self) -> np.ndarray:
        """ Get Processed results. """
        pass


class DataBridge(ABC):
    """ Applies processed data. """
    @abstractmethod
    def set_data(self, frame: int, data: np.ndarray):
        pass


class DataPipeline(ABC):
    provider: DataProvider
    processor: DataProcessor
    bridge: DataBridge

    def update(self):
        frame, data = self.provider.get_data()
        self.processor.set_data(data)
        data = self.processor.get_data()
        self.bridge.set_data(frame, data)
