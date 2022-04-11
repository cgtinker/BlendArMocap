from abc import ABC, abstractmethod
from pathlib import Path
import json


class BoneNameProvider(ABC):
    path = Path(__file__).parent / "data"

    @abstractmethod
    def provide_bone_names(self):
        pass

    def to_json(self, data, name):
        path = self.path / f"{name}.json"
        with open(path, 'w', encoding='utf-8') as f:
            j = json.dumps(data, ensure_ascii=False, indent=4, separators=(',', ':'))
            f.write(j)
        return j

    def from_json(self, name):
        path = self.path / f"{name}.json"
        with open(path) as f:
            j = json.load(f)
        return j

def main():
    pass

if __name__ == '__main__':
    main()