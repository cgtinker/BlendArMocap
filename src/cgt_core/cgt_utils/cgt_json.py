from __future__ import annotations
import json


class JsonData(object):
    """ Import json data, preferably as dict.
        Can load lists, will store them as dict with "data" as key. """
    data: dict = None

    def __init__(self, path: str = None, **data):
        if path:
            with open(path, 'rb') as jsonFile:
                data = json.load(jsonFile)

                if isinstance(data, dict):
                    self.__dict__.update((), **data)
                elif isinstance(data, list):
                    self.__dict__.update((), **{"data": data})
                else:
                    assert TypeError
        else:
            self.__dict__.update((), **data)

    def save(self, path: str = None):
        assert path is not None
        with open(path, "w", encoding='utf-8') as jsonFile:
            json.dump(self.__dict__, jsonFile, ensure_ascii=False, indent=4, separators=(',', ':'), sort_keys=False)

    def __str__(self):
        s = ["{"]

        def recv(d, depth=0):
            for k, v in d.items():
                if isinstance(v, dict):
                    tabs = "\t"*depth
                    s.append(f"\n{tabs}{k}: ")
                    s.append("{")
                    recv(v, depth+1)
                    tabs = "\t"*depth
                    s.append(f"\n{tabs}")
                    s.append("},")
                else:
                    tabs = "\t"*depth
                    s.append(f"\n{tabs}{k}: {v},")

        recv(self.__dict__, 1)
        s.append("\n}")
        return "".join(s)

    def __call__(self):
        return self.data
