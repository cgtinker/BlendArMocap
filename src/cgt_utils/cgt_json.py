import json


def to_json(data, path):
    print(path)
    with open(path, 'w', encoding='utf-8') as f:
        j = json.dumps(data, ensure_ascii=False, indent=4, sort_keys=True, separators=(',', ':'))
        f.write(j)
    return j


def from_json(path):
    with open(path) as f:
        j = json.load(f)
    return j
