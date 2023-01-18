from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Tuple, Any, Optional
from ..cgt_utils.cgt_timers import timeit
import logging


class Node(ABC):
    @abstractmethod
    def update(self, data: Any, frame: int) -> Tuple[Optional[Any], int]:
        pass

    def __str__(self):
        return self.__class__.__name__


class NodeChain(Node):
    nodes: List[Node]

    def __init__(self):
        self.nodes = list()

    # @timeit
    def update(self, data: Any, frame: int) -> Tuple[Optional[Any], int]:
        """ Nodes executed inside a chain. """
        for node in self.nodes:
            # logging.debug(f"{type(node)}, {node.__class__.__name__}.update()") #{data}, {frame})")
            if data is None:
                return None, frame

            data, frame = node.update(data, frame)
        return data, frame

    def append(self, node: Node):
        """ Appends node to the chain, order does matter. """
        self.nodes.append(node)

    def __str__(self):
        s = ""
        for node in self.nodes:
            s += str(node)
            s += " -> "
        return s[:-4]


class NodeChainGroup(Node):
    """ Node containing multiple node chains.
        Chains and input got to match
        Input == Output. """
    nodes: List[NodeChain]

    def __init__(self):
        self.nodes = list()

    # @timeit
    def update(self, data: Any, frame: int) -> Tuple[Optional[Any], int]:
        """ Push data in their designed node chains. """
        assert len(data) == len(self.nodes)

        updated_data = []
        for node_chain, chunk in zip(self.nodes, data):
            c, f = node_chain.update(chunk, frame)
            updated_data.append(c)

        return updated_data, frame

    def __str__(self):
        s = ""
        for node_chain in self.nodes:
            s += '\n\t -> '
            s += str(node_chain)
        return s


class InputNode(Node):
    """ Returns data on call. """
    @abstractmethod
    def update(self, data: None, frame: int) -> Tuple[Optional[Any], int]:
        pass


class CalculatorNode(Node):
    """ Calculate new data and changes the input shape. """
    @abstractmethod
    def update(self, data: Any, frame: int) -> Tuple[Optional[Any], int]:
        pass


class OutputNode(Node):
    """ Outputs and returns the data without changing values nor shape. """
    @abstractmethod
    def update(self, data: Any, frame: int) -> Tuple[Optional[Any], int]:
        pass
