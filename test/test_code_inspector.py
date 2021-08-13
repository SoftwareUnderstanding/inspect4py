import unittest
import shutil
from code_inspector.utils import *
from code_inspector.cli import *


class Test(unittest.TestCase):
    def test_extract_software_type(self):
        json = [{"type": "service",
                 "run": "python /GitHub/test_repos/Chowlk/app.py"},
                {"type": "script with main",
                 "run": "python /GitHub/test_repos/Chowlk/converter.py"}]
        type_script = extract_software_type(json)
        assert (type_script == "service")

    def test_extract_software_type_empty(self):
        json = []
        type_script = extract_software_type(json)
        assert (type_script == "not found")

    def test_call_list_super(self):
        dictionary = {'Rectangle': {}, 'Square': {'__init__': {'local': ['super_test.Rectangle.__init__']}}}
        input_path="./test_files/test_inheritance/super_test.py"
        output_dir="./output_dir"
        control_flow= False
        fig= False
        cf_dir, json_dir = create_output_dirs(output_dir, control_flow)
        code_info = CodeInspection(input_path, cf_dir, json_dir, fig, control_flow)
        call_list_data = call_list_file(code_info)
        shutil.rmtree(output_dir) 
        assert (call_list_data['Rectangle'] == dictionary['Rectangle'])
        assert (call_list_data['Square'] == dictionary['Square'])

    def test_call_list_nested(self):
        dictionary =  {'functions': {'test': {'local': ['nested_call.MyClass', 'nested_call.MyClass.func']}}, 'body': {'local': ['nested_call.test']}, 'MyClass': {'func': {'local': ['nested_call.MyClass.func.nested', 'print'], 'nested': {'nested': {'local': ['print']}}}}}
        input_path="./test_files/test_inheritance/nested_call.py"
        output_dir="./output_dir"
        control_flow= False
        fig= False
        cf_dir, json_dir = create_output_dirs(output_dir, control_flow)
        code_info = CodeInspection(input_path, cf_dir, json_dir, fig, control_flow)
        call_list_data = call_list_file(code_info)
        shutil.rmtree(output_dir) 
        assert (call_list_data == dictionary)


if __name__ == '__main__':
    unittest.main()
