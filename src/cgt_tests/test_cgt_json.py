import unittest
from src.cgt_core.cgt_utils.cgt_json import *


class TestJson(unittest.TestCase):
    def test_json(self):
        data = ['foo', {'bar': ('baz', None, 1.0, 2)}]
        path = "data/test_file.json"
        to_json(data, path)
        m_json = from_json(path)
        self.assertEqual(['foo', {'bar': ['baz', None, 1.0, 2]}], m_json)


if __name__ == '__main__':
    unittest.main()
