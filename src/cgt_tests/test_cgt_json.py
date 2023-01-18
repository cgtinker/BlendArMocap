import unittest
from src.cgt_core.cgt_utils.cgt_json import *


class TestJson(unittest.TestCase):
    def test_json_dict(self):
        path = "data/json_dict.json"
        data = JsonData(path=path)
        data.save(path)

    def test_json_list(self):
        path = "data/json_list.json"
        data = JsonData(path=path)
        data.save(path)


if __name__ == '__main__':
    unittest.main()
