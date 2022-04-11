from abc import ABC, abstractmethod
from pathlib import Path
import json


class BoneNameProvider(ABC):
    @abstractmethod
    def provide_bone_names(self):
        pass

    @staticmethod
    def to_json(data, path):
        with open(path, 'w', encoding='utf-8') as f:
            j = json.dumps(data, ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ':'))
            f.write(j)
        return j

    @staticmethod
    def from_json(path):
        with open(path) as f:
            j = json.load(f)
        return j


def main():
    priv = BoneNameProvider()
    json = priv.from_json("")
    print(json['hands']['index_finger_dip.L'])


if __name__ == '__main__':
    main()