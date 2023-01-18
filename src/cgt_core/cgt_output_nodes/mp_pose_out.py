from __future__ import annotations
from . import mp_out_utils
from ..cgt_naming import COLLECTIONS, cgt_defaults
from ..cgt_bpy import cgt_bpy_utils, cgt_collection, cgt_object_prop


class MPPoseOutputNode(mp_out_utils.BpyOutputNode):
    pose = []
    col_name = COLLECTIONS.pose
    parent_col = COLLECTIONS.drivers

    def __init__(self):
        data = cgt_defaults
        references = {}
        for k, v in data.pose.items():
            references[k] = v

        self.pose = cgt_bpy_utils.add_empties(references, 0.005, suffix='cgt_')
        for ob in self.pose:
            cgt_object_prop.set_custom_property(ob, "cgt_id", data.identifier)

        cgt_collection.add_list_to_collection(self.col_name, self.pose, self.parent_col)

    def update(self, data, frame):
        loc, rot, sca = data
        for data, method in zip([loc, rot, sca], [self.translate, self.euler_rotate, self.scale]):
            try:
                method(self.pose, data, frame)
            except IndexError:
                pass
        return data, frame

