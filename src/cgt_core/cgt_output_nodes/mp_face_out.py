from __future__ import annotations
from . import mp_out_utils
from ..cgt_naming import COLLECTIONS, cgt_defaults
from ..cgt_bpy import cgt_bpy_utils, cgt_collection, cgt_object_prop


class MPFaceOutputNode(mp_out_utils.BpyOutputNode):
    face = []
    col_name = COLLECTIONS.face
    parent_col = COLLECTIONS.drivers

    def __init__(self):
        data = cgt_defaults

        references = {}
        for i in range(468):
            references[f'{i}'] = f"cgt_face_vertex_{i}"
        for k, name in data.face.items():
            references[f'{468+int(k)}'] = name

        self.face = cgt_bpy_utils.add_empties(references, 0.005)
        for ob in self.face[468:]:
            cgt_object_prop.set_custom_property(ob, "cgt_id", data.identifier)

        cgt_collection.add_list_to_collection(self.col_name, self.face[468:], self.parent_col)
        cgt_collection.add_list_to_collection(self.col_name+"_DATA", self.face[:468], self.col_name)

    def update(self, data, frame):
        loc, rot, sca = data
        for data, method in zip([loc, rot, sca], [self.translate, self.euler_rotate, self.scale]):
            try:
                method(self.face, data, frame)
            except IndexError:
                pass
        return data, frame

