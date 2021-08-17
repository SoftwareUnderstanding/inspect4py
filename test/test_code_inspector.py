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

    def test_call_list_super_test_5(self):
        dictionary={'functions': {}, 'body': {'local': ['super_test_5.Cube', 'super_test_5.Cube.surface_area', 'super_test_5.VolumeMixin.volume']}, 'Rectangle': {}, 'Square': {'__init__': {'local': ['super_test_5.Rectangle.__init__']}}, 'VolumeMixin': {'volume': {'local': ['super_test_5.VolumeMixin.area']}}, 'Cube': {'__init__': {'local': ['super_test_5.Square.__init__']}, 'face_area': {'local': ['super_test_5.Rectangle.area']}, 'surface_area': {'local': ['super_test_5.Rectangle.area']}}}
        input_path="./test_files/test_inheritance/super_test_5.py"
        output_dir="./output_dir"
        control_flow= False
        fig= False
        cf_dir, json_dir = create_output_dirs(output_dir, control_flow)
        code_info = CodeInspection(input_path, cf_dir, json_dir, fig, control_flow)
        call_list_data = call_list_file(code_info)
        shutil.rmtree(output_dir) 
        assert (call_list_data['body'] == dictionary['body'])

    def test_call_list_nested(self):
        dictionary = {'functions': {'test': {'local': ['nested_call.MyClass', 'nested_call.MyClass.func']}}, 'body': {'local': ['nested_call.test']}, 'MyClass': {'func': {'local': ['nested_call.MyClass.func.nested'], 'nested': {'nested': {'local': ['print']}}}}}
        input_path="./test_files/test_inheritance/nested_call.py"
        output_dir="./output_dir"
        control_flow= False
        fig= False
        cf_dir, json_dir = create_output_dirs(output_dir, control_flow)
        code_info = CodeInspection(input_path, cf_dir, json_dir, fig, control_flow)
        call_list_data = call_list_file(code_info)
        shutil.rmtree(output_dir) 
        assert (call_list_data == dictionary)

    def test_call_list_super_nested(self):
        dictionary={'functions': {'func_d': {'local': ['super_nested_call.func_d.func_e'], 'nested': {'func_e': {'local': ['print']}}}, 'main': {'local': ['super_nested_call.MyClass', 'super_nested_call.MyClass.func_a', 'super_nested_call.func_d']}}, 'body': {}, 'MyClass': {'func_a': {'local': ['print', 'super_nested_call.MyClass.func_a.func_b'], 'nested': {'func_b': {'local': ['print', 'super_nested_call.MyClass.func_a.func_b.func_c'], 'nested': {'func_c': {'local': ['print']}}}}}}}
        input_path="./test_files/test_inheritance/super_nested_call.py"
        output_dir="./output_dir"
        control_flow= False
        fig= False
        cf_dir, json_dir = create_output_dirs(output_dir, control_flow)
        code_info = CodeInspection(input_path, cf_dir, json_dir, fig, control_flow)
        call_list_data = call_list_file(code_info)
        shutil.rmtree(output_dir) 
        assert (call_list_data == dictionary)

    def test_call_list_import(self):
        dictionary = {'functions': {'funct_D': {'local': ['print', 'test_functions.funct_A']}}, 'body': {'local': ['test_classes.MyClass_A', 'test_classes.MyClass_B', 'test_import.MyClass_D', 'test_import.funct_D', 'test_functions.funct_A', 'test_import.funct_D', 'test_classes.MyClass_C']}, 'MyClass_D': {'__init__': {'local': ['print', 'test_functions.funct_C', 'test_import.funct_D', 'test_import.MyClass_E']}}, 'MyClass_E': {'__init__': {'local': ['print', 'test_classes.MyClass_B']}}}
        input_path="./test_files/test_inheritance/test_import.py"
        output_dir="./output_dir"
        control_flow= False
        fig= False
        cf_dir, json_dir = create_output_dirs(output_dir, control_flow)
        code_info = CodeInspection(input_path, cf_dir, json_dir, fig, control_flow)
        call_list_data = call_list_file(code_info)
        shutil.rmtree(output_dir) 
        assert (call_list_data == dictionary)
    
    def test_call_list_external_module(self):
        dictionary={'body': {'local': ['random.seed', 'print', 'random.random', 'random.random', 'random.random', 'random.seed', 'print', 'random.random', 'random.random', 'random.random']}}
        input_path="./test_files/test_random.py"
        output_dir="./output_dir"
        control_flow= False
        fig= False
        cf_dir, json_dir = create_output_dirs(output_dir, control_flow)
        code_info = CodeInspection(input_path, cf_dir, json_dir, fig, control_flow)
        call_list_data = call_list_file(code_info)
        shutil.rmtree(output_dir) 
        assert (call_list_data['body'] == dictionary['body'])


    def test_call_list_argument_call(self):
        dictionary={'functions': {'func_1': {'local': ['print', 'argument_call.func_2']}}, 'body': {'local': ['print', 'argument_call.func_1', 'argument_call.MyClass.func_a']}, 'MyClass': {'func_a': {'local': ['print', 'argument_call.MyClass.func_b']}}}
        input_path="./test_files/test_dynamic/argument_call.py"
        output_dir="./output_dir"
        control_flow= False
        fig= False
        cf_dir, json_dir = create_output_dirs(output_dir, control_flow)
        code_info = CodeInspection(input_path, cf_dir, json_dir, fig, control_flow)
        call_list_data = call_list_file(code_info)
        shutil.rmtree(output_dir) 
        assert (call_list_data['body'] == dictionary['body'])

    def test_call_list_dynamic(self):
        dictionary={'functions': {'func_2': {'local': ['test_dynamic.func_1']}}, 'body': {'local': ['test_dynamic.func_2', 'print']}}
        input_path="./test_files/test_dynamic/test_dynamic.py"
        output_dir="./output_dir"
        control_flow= False
        fig= False
        cf_dir, json_dir = create_output_dirs(output_dir, control_flow)
        code_info = CodeInspection(input_path, cf_dir, json_dir, fig, control_flow)
        call_list_data = call_list_file(code_info)
        shutil.rmtree(output_dir) 
        assert (call_list_data['body'] == dictionary['body'])


if __name__ == '__main__':
    unittest.main()


