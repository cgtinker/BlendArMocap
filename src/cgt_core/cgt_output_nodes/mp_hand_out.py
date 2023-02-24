from __future__ import annotations
from . import mp_out_utils
from ..cgt_naming import COLLECTIONS, cgt_defaults
from ..cgt_bpy import cgt_bpy_utils, cgt_collection, cgt_object_prop


class CgtMPHandOutNode(mp_out_utils.BpyOutputNode):
    left_hand = []
    right_hand = []
    col_name = COLLECTIONS.hands
    parent_col = COLLECTIONS.drivers

    def __init__(self):
        data = cgt_defaults
        references = data.hand
        self.left_hand = cgt_bpy_utils.add_empties(references, 0.005, prefix=".L", suffix='cgt_')
        self.right_hand = cgt_bpy_utils.add_empties(references, 0.005, prefix=".R", suffix='cgt_')

        for ob in self.left_hand+self.right_hand:
            cgt_object_prop.set_custom_property(ob, "cgt_id", data.identifier)

        cgt_collection.create_collection(self.col_name+"S", self.parent_col)
        cgt_collection.create_collection(self.col_name+".L", self.col_name+"S")
        cgt_collection.create_collection(self.col_name+".R", self.col_name+"S")
        cgt_collection.add_list_to_collection(self.col_name+".L", self.left_hand, self.parent_col)
        cgt_collection.add_list_to_collection(self.col_name+".R", self.right_hand, self.parent_col)

    def split(self, data):
        left_hand_data, right_hand_data = data
        return [[self.left_hand, left_hand_data], [self.right_hand, right_hand_data]]

    def update(self, data, frame):
        loc, rot, sca = data
        for data, method in zip([loc, rot, sca], [self.translate, self.euler_rotate, self.scale]):
            for hand, chunk in self.split(data):
                try:
                    method(hand, chunk, frame)
                except IndexError:
                    pass
        return data, frame
