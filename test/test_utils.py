import unittest
from inspect4py.utils import *


class Test(unittest.TestCase):
    def test_extract_software_type(self):
        json_test = [
            {"type": "service", "run": "python /GitHub/test_repos/Chowlk/app.py"},
            {"type": "script with main", "run": "python /GitHub/test_repos/Chowlk/converter.py"}
        ]
        type_script = rank_software_invocation(json_test)
        assert (type_script[0]["type"] == "service")

    def test_extract_software_type_empty(self):
        json = []
        type_script = rank_software_invocation(json)
        assert (type_script == [])


if __name__ == '__main__':
    unittest.main()