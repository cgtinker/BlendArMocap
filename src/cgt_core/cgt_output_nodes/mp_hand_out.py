from __future__ import annotations
from dataclasses import asdict
from . import bpy_out_utils
from ..cgt_naming import *
from ..cgt_bpy import cgt_bpy_utils, cgt_collection


class CgtMPHandOutNode(bpy_out_utils.BpyOutputNode):
    left_hand = []
    right_hand = []
    col_name = COLLECTIONS.hands
    parent_col = COLLECTIONS.drivers

    def __init__(self):
        references = {idx: val for idx, val in enumerate(asdict(HAND()).values())}
        self.left_hand = cgt_bpy_utils.add_empties(references, 0.005, ".L")
        self.right_hand = cgt_bpy_utils.add_empties(references, 0.005, ".R")
        cgt_collection.add_list_to_collection(self.col_name, self.left_hand, self.parent_col)
        cgt_collection.add_list_to_collection(self.col_name, self.right_hand, self.parent_col)

    def split(self, data):
        left_hand_data, right_hand_data = data
        return [[self.left_hand, left_hand_data], [self.right_hand, right_hand_data]]

    def update(self, *args):
        loc, rot, sca, frame = args
        for data, method in zip([loc, rot, sca], [self.translate, self.euler_rotate, self.scale]):
            for hand, chunk in self.split(data):
                try:
                    method(hand, chunk, frame)
                except IndexError:
                    pass
