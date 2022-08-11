import json


class JsonParser(object):
    """ Parses json mediapipe detection data, the data has to be stored
        with a descriptor. Sample:
        {'POSE':
            {   '0': {'x': 0.745145, 'y': 0.562732, 'z': -1.13462},
                '1': {'x': 0.784312, 'y': 0.494899, 'z': -1.06639},
                ...
            }
        }
        {'HAND':
            {
                "0":
                {
                    '0': {'x': 0.745145, 'y': 0.562732, 'z': -1.13462},
                    '1': {'x': 0.784312, 'y': 0.494899, 'z': -1.06639},
                    ...
                },
                "1":
                {
                    ...
                }
            }
        }
    """
    detection_type: str = None
    detection_types: list = ["FACE", "HANDS", "POSE", "HOLISTIC"]
    detection_contents: dict = {
        "FACE": 468,
        "POSE": 33,
        "HANDS": [21, 21],
        "HOLISTIC": [21, 21, 468, 33],
    }

    def exec(self, data):
        json_data = json.loads(data)
        self.get_detection_type(json_data)
        res = self.construct_array(json_data[self.detection_type])
        return res

    def construct_array(self, data):
        res = []
        descriptor = self.detection_contents[self.detection_type]
        if isinstance(descriptor, int):
            res = self.array_from_int(data, descriptor)
        elif isinstance(descriptor, list):
            res = self.array_from_list(data, descriptor)

        # some manual parsing to receive the weird mp shape
        if self.detection_type == "FACE":
            return [res]
        elif self.detection_type == "HANDS":
            return self.weird_hands(res[0], res[1])
        elif self.detection_type == "HOLISTIC":
            # lhand, rhand, face, pose
            return [self.weird_hands(res[0], res[1]), [res[2]], res[3]]
        return res

    def weird_hands(self, left_hand, right_hand):
        arr = []
        for hand in [left_hand, right_hand]:
            if len(hand) > 0:
                arr.append([hand])
            else:
                arr.append([])
        return arr

    def array_from_list(self, data, descriptor):
        arr = []
        for idx, size in enumerate(descriptor):
            sub_arr = self.array_from_int(data[str(idx)], size)
            arr.append(sub_arr)
        return arr

    @staticmethod
    def array_from_int(data, length):
        arr = []
        for i in range(0, length):
            sub_arr = []
            try:
                for j in ["x", "y", "z"]:
                    sub_arr.append(data[str(i)][j])
                arr.append([i, sub_arr])
            except KeyError:
                break

        return arr

    def get_detection_type(self, data):
        if self.detection_type:
            return self.detection_type

        for detection_type in self.detection_types:
            if detection_type in data:
                self.detection_type = detection_type

