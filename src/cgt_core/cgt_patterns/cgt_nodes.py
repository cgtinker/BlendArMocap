from __future__ import annotations
import numpy as np
from abc import ABC, abstractmethod
from typing import List


class Node(ABC):
    @abstractmethod
    def update(self, data) -> np.ndarray:
        pass


class NodeChain(Node):
    nodes: List[Node]

    def update(self, data) -> np.ndarray:
        """ Node chain executed inside a chain. """
        for node in self.nodes:
            data = node.update(data)
        return data

    def add_node(self, node: Node):
        """ Adds nodes in the chain, order does matter. """
        self.nodes.append(node)


class InputNode(Node):
    """ Outputs data on get request. """
    @abstractmethod
    def update(self, frame: int) -> np.ndarray:
        pass


class IntersectionNode(Node):
    """ Node which splits up input data and pushes it to node chains. """
    nodes: List[Node]

    @abstractmethod
    def update(self, data: np.ndarray) -> np.ndarray:
        pass

    @abstractmethod
    def split(self):
        pass


class ReshapeNode(Node):
    """ Reshapes data to match processing requirements. """
    @abstractmethod
    def update(self, data: np.ndarray) -> np.ndarray:
        pass


class CalculatorNode(Node):
    """ Calculate new data and changes the input shape. """
    @abstractmethod
    def update(self, data: np.ndarray) -> np.ndarray:
        pass


class OutputNode(Node):
    """ Outputs the data without changing values nor shape. """
    @abstractmethod
    def update(self, data: np.ndarray) -> np.ndarray:
        pass
