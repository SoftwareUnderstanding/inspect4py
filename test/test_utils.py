import unittest
from code_inspector.utils import *


class Test(unittest.TestCase):
    def test_extract_software_type(self):
        json_test = [
            {"type": "service", "run": "python /GitHub/test_repos/Chowlk/app.py"},
            {"type": "script with main", "run": "python /GitHub/test_repos/Chowlk/converter.py"}
        ]
        type_script = extract_software_type(json_test)
        assert (type_script == "service")

    def test_extract_software_type_empty(self):
        json = []
        type_script = extract_software_type(json)
        assert (type_script == "not found")


if __name__ == '__main__':
    unittest.main()