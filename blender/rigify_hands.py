from utils import log
from blender import abs_rigging
import importlib

importlib.reload(abs_rigging)


class RigifyHands(abs_rigging.BpyRigging):
    def __init__(self):
        # tips naming convention in rigify has some flaws?
        self.references = {
            0: "hand_fk",
            1: "thumb.01",
            2: "thumb.02",
            3: "thumb.03",
            4: "thumb.01.L.001",
            5: "f_index.01",
            6: "f_index.02",
            7: "f_index.03",
            8: "f_index.01",
            9: "f_middle.01",
            10: "f_middle.02",
            11: "f_middle.03",
            12: "f_middle.01",
            13: "f_ring.01",
            14: "f_ring.02",
            15: "f_ring.03",
            16: "f_ring.01",
            17: "f_pinky.01",
            18: "f_pinky.02",
            19: "f_pinky.03",
            20: "f_pinky.01",
        }

        self.relation_dict = {}
        self.extension = ""

    def get_reference_bone(self, key):
        if "TIP" in key:
            ref = self.references[key] + self.extension + ".001"
            return ref

        ref = self.references[key] + self.extension
        return ref

    def set_relation_dict(self, hand_empties):
        # left or right hand
        if ".L" in hand_empties[0]:
            self.extension = ".L"
        elif ".R" in hand_empties[0]:
            self.extension = ".R"
        
        for empty in hand_empties:
            # remove extension
            name = empty.name.replace(self.extension, "")
            try:
                self.relation_dict[self.get_reference_bone(name)] = empty
            except KeyError:
                log.logger.Error("Driver empty does not exist: ", empty.name)

