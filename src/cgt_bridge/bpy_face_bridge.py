from . import bpy_bridge_interface
from ..cgt_blender.utils import objects
from ..cgt_naming import FACE, COLLECTIONS


class BpyFaceReferences(bpy_bridge_interface.BpyInstanceProvider):
    face = []
    custom_data_arr = []
    col_name = COLLECTIONS.face

    def __init__(self):
        references = {}
        for i in range(468):
            references[f'{i}'] = f"{FACE.face}{i}"

        # face empties (default data)
        self.face = objects.add_empties(references, 0.005)
        objects.add_list_to_collection(self.col_name, self.face, self.parent_col)

        # objects for drivers
        mapping_references = [FACE.right_eye_t, FACE.right_eye_b,
                              FACE.left_eye_t, FACE.left_eye_b,
                              FACE.mouth_t, FACE.mouth_b,
                              FACE.mouth_r, FACE.mouth_l,

                              FACE.eyebrow_in_l, FACE.eyebrow_mid_l,
                              FACE.eyebrow_out_l,
                              FACE.eyebrow_in_r, FACE.eyebrow_mid_r,
                              FACE.eyebrow_out_r
                              ]
        mapping_objs = [objects.add_empty(0.01, name) for name in mapping_references]
        objects.add_list_to_collection(self.col_name, mapping_objs, self.parent_col)

        # custom data for assignment during processing
        # position values currently doesn't get used
        custom_data_array = [
            [bpy_bridge_interface.CustomData(),
             0.002, prop[0], "CUBE", prop[1]] for prop in [[FACE.head, [0, 0, 0]],
                                                           [FACE.mouth, [0, -.1, -1]],
                                                           [FACE.mouth_corners, [0, -.1, -.1]],
                                                           [FACE.left_eye, [-.05, -.05, -.075]],
                                                           [FACE.right_eye, [.05, .05, .075]],
                                                           [FACE.chin, [.0, -.05, -.25]],
                                                           [FACE.left_eyebrow, [.05, 0, .1]],
                                                           [FACE.right_eyebrow, [-.05, 0, .1]]]]

        # init custom data objects
        [self.init_bpy_driver_obj(
            e[0], self.face, e[1], e[2], self.col_name, e[3], e[4]) for e in custom_data_array]
        self.custom_data_arr = [custom_data[0] for custom_data in custom_data_array]

        # setting starting position for custom data isn't that pretty
        # data = [[e[0].idx, e[4]] for e in custom_data_array]
        # self.translate(self.face, data, 0)

    def get_instances(self):
        return self.face, self.custom_data_arr

    def set_position(self, data, frame):
        """Keyframes the position of input data."""
        try:
            self.translate(self.face, data, frame)
        except IndexError:
            print("VALUE ERROR WHILE ASSIGNING FACE POSITION")

    def set_rotation(self, data, frame):
        """ Apply rotation data. """
        self.euler_rotate(self.face, data, frame)

    def set_scale(self, data, frame):
        """ Apply scale data. """
        self.scale(self.face, data, frame)