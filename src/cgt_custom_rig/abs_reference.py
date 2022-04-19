from abc import ABC, abstractmethod
from pathlib import Path
from ..cgt_utils import json_utils


class BoneNameProvider(ABC):
    path = Path(__file__).parent / "data"

    @abstractmethod
    def provide_bone_names(self):
        pass

    def to_json(self, data, name):
        path = self.path / f"{name}.json"
        j = json_utils.to_json(data, path)
        return j

    def from_json(self, name):
        path = self.path / f"{name}.json"
        j = json_utils.from_json(path)
        return j


def main():
    path = Path(__file__).parent / "data"
    path = path / f"hands.json"
    j = json_utils.from_json(path)
    print(j)


if __name__ == '__main__':
    main()
