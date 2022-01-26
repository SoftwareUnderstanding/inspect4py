import unittest
import shutil
from inspect4py.cli import *
from inspect4py import cli, utils


class Test(unittest.TestCase):

    def test_call_list_super(self):
        dictionary = {'Rectangle': {}, 'Square': {'__init__': {'local': ['super_test.Rectangle.__init__']}}}
        input_path = "./test_files/test_inheritance/super_test.py"
        output_dir = "./output_dir"
        control_flow = False
        fig = False
        cf_dir, json_dir = create_output_dirs(output_dir, control_flow)
        code_info = CodeInspection(input_path, cf_dir, json_dir, fig, control_flow)
        call_list_data = call_list_file(code_info)
        shutil.rmtree(output_dir)
        assert (call_list_data['Rectangle'] == dictionary['Rectangle'])
        assert (call_list_data['Square'] == dictionary['Square'])

    def test_call_list_super_test_5(self):
        dictionary = {'functions': {}, 'body': {
            'local': ['super_test_5.Cube', 'super_test_5.Cube.surface_area', 'super_test_5.VolumeMixin.volume']},
                      'Rectangle': {}, 'Square': {'__init__': {'local': ['super_test_5.Rectangle.__init__']}},
                      'VolumeMixin': {'volume': {'local': ['super_test_5.VolumeMixin.area']}},
                      'Cube': {'__init__': {'local': ['super_test_5.Square.__init__']},
                               'face_area': {'local': ['super_test_5.Rectangle.area']},
                               'surface_area': {'local': ['super_test_5.Rectangle.area']}}}
        input_path = "./test_files/test_inheritance/super_test_5.py"
        output_dir = "./output_dir"
        control_flow = False
        fig = False
        cf_dir, json_dir = create_output_dirs(output_dir, control_flow)
        code_info = CodeInspection(input_path, cf_dir, json_dir, fig, control_flow)
        call_list_data = call_list_file(code_info)
        shutil.rmtree(output_dir)
        assert (call_list_data['body'] == dictionary['body'])

    def test_call_list_nested(self):
        dictionary = {'functions': {'test': {'local': ['nested_call.MyClass', 'nested_call.MyClass.func']}},
                      'body': {'local': ['nested_call.test']}, 'MyClass': {
                'func': {'local': ['nested_call.MyClass.func.nested'], 'nested': {'nested': {'local': ['print']}}}}}
        input_path = "./test_files/test_inheritance/nested_call.py"
        output_dir = "./output_dir"
        control_flow = False
        fig = False
        cf_dir, json_dir = create_output_dirs(output_dir, control_flow)
        code_info = CodeInspection(input_path, cf_dir, json_dir, fig, control_flow)
        call_list_data = call_list_file(code_info)
        shutil.rmtree(output_dir)
        assert (call_list_data == dictionary)

    def test_call_list_super_nested(self):
        dictionary = {'functions': {
            'func_d': {'local': ['super_nested_call.func_d.func_e'], 'nested': {'func_e': {'local': ['print']}}},
            'main': {'local': ['super_nested_call.MyClass', 'super_nested_call.MyClass.func_a',
                               'super_nested_call.func_d']}}, 'body': {}, 'MyClass': {
            'func_a': {'local': ['print', 'super_nested_call.MyClass.func_a.func_b'], 'nested': {
                'func_b': {'local': ['print', 'super_nested_call.MyClass.func_a.func_b.func_c'],
                           'nested': {'func_c': {'local': ['print']}}}}}}}
        input_path = "./test_files/test_inheritance/super_nested_call.py"
        output_dir = "./output_dir"
        control_flow = False
        fig = False
        cf_dir, json_dir = create_output_dirs(output_dir, control_flow)
        code_info = CodeInspection(input_path, cf_dir, json_dir, fig, control_flow)
        call_list_data = call_list_file(code_info)
        shutil.rmtree(output_dir)
        assert (call_list_data == dictionary)

    def test_call_list_import(self):
        dictionary = {'functions': {'funct_D': {'local': ['print', 'test_functions.funct_A']}}, 'body': {
            'local': ['test_classes.MyClass_A', 'test_classes.MyClass_B', 'test_import.MyClass_D',
                      'test_import.funct_D', 'test_functions.funct_A', 'test_import.funct_D',
                      'test_classes.MyClass_C']}, 'MyClass_D': {
            '__init__': {'local': ['print', 'test_functions.funct_C', 'test_import.funct_D', 'test_import.MyClass_E']}},
                      'MyClass_E': {'__init__': {'local': ['print', 'test_classes.MyClass_B']}}}
        input_path = "./test_files/test_inheritance/test_import.py"
        output_dir = "./output_dir"
        control_flow = False
        fig = False
        cf_dir, json_dir = create_output_dirs(output_dir, control_flow)
        code_info = CodeInspection(input_path, cf_dir, json_dir, fig, control_flow)
        call_list_data = call_list_file(code_info)
        shutil.rmtree(output_dir)
        assert (call_list_data == dictionary)

    def test_call_list_external_module(self):
        dictionary = {'body': {
            'local': ['random.seed', 'print', 'random.random', 'random.random', 'random.random', 'random.seed', 'print',
                      'random.random', 'random.random', 'random.random']}}
        input_path = "./test_files/test_random.py"
        output_dir = "./output_dir"
        control_flow = False
        fig = False
        cf_dir, json_dir = create_output_dirs(output_dir, control_flow)
        code_info = CodeInspection(input_path, cf_dir, json_dir, fig, control_flow)
        call_list_data = call_list_file(code_info)
        shutil.rmtree(output_dir)
        assert (call_list_data['body'] == dictionary['body'])

    def test_call_list_argument_call(self):
        dictionary = {'functions': {'func_1': {'local': ['print', 'argument_call.func_2']}},
                      'body': {'local': ['print', 'argument_call.func_1', 'argument_call.MyClass.func_a']},
                      'MyClass': {'func_a': {'local': ['print', 'argument_call.MyClass.func_b']}}}
        input_path = "./test_files/test_dynamic/argument_call.py"
        output_dir = "./output_dir"
        control_flow = False
        fig = False
        cf_dir, json_dir = create_output_dirs(output_dir, control_flow)
        code_info = CodeInspection(input_path, cf_dir, json_dir, fig, control_flow)
        call_list_data = call_list_file(code_info)
        shutil.rmtree(output_dir)
        assert (call_list_data['body'] == dictionary['body'])

    def test_call_list_dynamic_body(self):
        dictionary = {'functions': {'func_2': {'local': ['test_dynamic.func_1']}},
                      'body': {'local': ['test_dynamic.func_2', 'print']}}
        input_path = "./test_files/test_dynamic/test_dynamic.py"
        output_dir = "./output_dir"
        control_flow = False
        fig = False
        cf_dir, json_dir = create_output_dirs(output_dir, control_flow)
        code_info = CodeInspection(input_path, cf_dir, json_dir, fig, control_flow)
        call_list_data = call_list_file(code_info)
        shutil.rmtree(output_dir)
        assert (call_list_data == dictionary)

    def test_call_list_dynamic_func(self):
        dictionary = {'functions': {'func_2': {'local': ['test_dynamic_func.func_1']},
                                    'main': {'local': ['test_dynamic_func.func_2', 'print']}}, 'body': {}}
        input_path = "./test_files/test_dynamic/test_dynamic_func.py"
        output_dir = "./output_dir"
        control_flow = False
        fig = False
        cf_dir, json_dir = create_output_dirs(output_dir, control_flow)
        code_info = CodeInspection(input_path, cf_dir, json_dir, fig, control_flow)
        call_list_data = call_list_file(code_info)
        shutil.rmtree(output_dir)
        assert (call_list_data == dictionary)

    def test_call_list_dynamic_body_import(self):
        dictionary = {'functions': {'func_3': {'local': ['test_dynamic_func.func_1']}},
                      'body': {'local': ['test_dynamic_import.func_3', 'print']}}
        input_path = "./test_files/test_dynamic/test_dynamic_import.py"
        output_dir = "./output_dir"
        control_flow = False
        fig = False
        cf_dir, json_dir = create_output_dirs(output_dir, control_flow)
        code_info = CodeInspection(input_path, cf_dir, json_dir, fig, control_flow)
        call_list_data = call_list_file(code_info)
        shutil.rmtree(output_dir)
        assert (call_list_data == dictionary)

    def test_call_list_dynamic_body_from_import(self):
        dictionary = {'functions': {'func_3': {'local': ['test_dynamic_func.func_1']}},
                      'body': {'local': ['test_dynamic_from_import.func_3', 'print']}}
        input_path = "./test_files/test_dynamic/test_dynamic_from_import.py"
        output_dir = "./output_dir"
        control_flow = False
        fig = False
        cf_dir, json_dir = create_output_dirs(output_dir, control_flow)
        code_info = CodeInspection(input_path, cf_dir, json_dir, fig, control_flow)
        call_list_data = call_list_file(code_info)
        shutil.rmtree(output_dir)
        assert (call_list_data == dictionary)

    def test_call_list_dynamic_import_alias(self):
        dictionary = {'functions': {'func_3': {'local': ['test_dynamic_func.td.func_1']}},
                      'body': {'local': ['test_dynamic_import_alias.func_3', 'print']}}
        input_path = "./test_files/test_dynamic/test_dynamic_import_alias.py"
        output_dir = "./output_dir"
        control_flow = False
        fig = False
        cf_dir, json_dir = create_output_dirs(output_dir, control_flow)
        code_info = CodeInspection(input_path, cf_dir, json_dir, fig, control_flow)
        call_list_data = call_list_file(code_info)
        shutil.rmtree(output_dir)
        assert (call_list_data == dictionary)

    def test_call_list_dynamic_import_method(self):
        dictionary = {'functions': {'func_2': {'local': ['test_dynamic_method.MyClass.func_1']}, 'main': {
            'local': ['test_dynamic_method.func_2', 'print', 'test_dynamic_method.MyClass']}}, 'body': {},
                      'MyClass': {}}
        input_path = "./test_files/test_dynamic/test_dynamic_method.py"
        output_dir = "./output_dir"
        control_flow = False
        fig = False
        cf_dir, json_dir = create_output_dirs(output_dir, control_flow)
        code_info = CodeInspection(input_path, cf_dir, json_dir, fig, control_flow)
        call_list_data = call_list_file(code_info)
        shutil.rmtree(output_dir)
        assert (call_list_data == dictionary)

    def test_call_list_dynamic_import_method_variable(self):
        dictionary = {'functions': {'func_2': {'local': ['test_dynamic_method_variable.MyClass.func_1']}, 'main': {
            'local': ['test_dynamic_method_variable.MyClass', 'test_dynamic_method_variable.func_2', 'print']}},
                      'body': {}, 'MyClass': {}}
        input_path = "./test_files/test_dynamic/test_dynamic_method_variable.py"
        output_dir = "./output_dir"
        control_flow = False
        fig = False
        cf_dir, json_dir = create_output_dirs(output_dir, control_flow)
        code_info = CodeInspection(input_path, cf_dir, json_dir, fig, control_flow)
        call_list_data = call_list_file(code_info)
        shutil.rmtree(output_dir)
        assert (call_list_data == dictionary)

    def test_call_list_dynamic_class_import(self):
        dictionary = {'functions': {}, 'body': {
            'local': ['test_dynamic_class_import.MyClass', 'test_dynamic_class_import.MyClass.func_3']},
                      'MyClass': {'func_3': {'local': ['test_dynamic_func.func_1']}}}
        input_path = "./test_files/test_dynamic/test_dynamic_class_import.py"
        output_dir = "./output_dir"
        control_flow = False
        fig = False
        cf_dir, json_dir = create_output_dirs(output_dir, control_flow)
        code_info = CodeInspection(input_path, cf_dir, json_dir, fig, control_flow)
        call_list_data = call_list_file(code_info)
        shutil.rmtree(output_dir)
        assert (call_list_data == dictionary)

    def test_service(self):
        input_path = "./test_files/Chowlk"
        output_dir = "./output_dir"
        fig = False
        ignore_dir_pattern = [".", "__pycache__"]
        ignore_file_pattern = [".", "__pycache__"]
        requirements = False
        call_list = False
        control_flow = False
        directory_tree = False
        software_invocation = True
        dir_info = invoke_inspector(input_path, fig, output_dir, ignore_dir_pattern, ignore_file_pattern, requirements,
                                    call_list, control_flow, directory_tree, software_invocation)
        current_type = dir_info['software_type']
        shutil.rmtree(output_dir)
        assert current_type[0]["type"] == "service"

    def test_package(self):
        input_path = "./test_files/somef"
        output_dir = "./output_dir"
        fig = False
        ignore_dir_pattern = [".", "__pycache__"]
        ignore_file_pattern = [".", "__pycache__"]
        requirements = False
        call_list = False
        control_flow = False
        directory_tree = False
        software_invocation = True
        dir_info = invoke_inspector(input_path, fig, output_dir, ignore_dir_pattern, ignore_file_pattern, requirements,
                                    call_list, control_flow, directory_tree, software_invocation)
        current_type = dir_info['software_type']
        shutil.rmtree(output_dir)
        assert current_type[0]["type"] == "package"

    def test_library(self):
        input_path = "./test_files/pylops"
        output_dir = "./output_dir"
        fig = False
        ignore_dir_pattern = [".", "__pycache__"]
        ignore_file_pattern = [".", "__pycache__"]
        requirements = False
        call_list = False
        control_flow = False
        directory_tree = False
        software_invocation = True
        dir_info = invoke_inspector(input_path, fig, output_dir, ignore_dir_pattern, ignore_file_pattern, requirements,
                                    call_list, control_flow, directory_tree, software_invocation)
        current_type = dir_info['software_type']
        shutil.rmtree(output_dir)
        assert current_type[0]["type"] == "library"

    def test_script(self):
        input_path = "./test_files/BoostingMonocularDepth"
        output_dir = "./output_dir"
        fig = False
        ignore_dir_pattern = [".", "__pycache__"]
        ignore_file_pattern = [".", "__pycache__"]
        requirements = False
        call_list = False
        control_flow = False
        directory_tree = False
        software_invocation = True
        dir_info = invoke_inspector(input_path, fig, output_dir, ignore_dir_pattern, ignore_file_pattern, requirements,
                                    call_list, control_flow, directory_tree, software_invocation)
        current_type = dir_info['software_type']
        shutil.rmtree(output_dir)
        assert current_type[0]["type"] == "script"

# Test for testing ast trees
#     def test_issue_110():
#         output_html_file = "test_issue_110_output.html"
#         self.assertEquals(3, 4)
#         m = MakeDocco(input_data_file="test_issue_110_input.ttl")
#         m.document(destination=output_html_file)
#         assert "balance between £1,000 and £1,000,000 GBP" in open(output_html_file).read()

# def crop_transform68(rimg, landmark, image_size, src):
#
#     assert landmark.shape[0] == 68 or landmark.shape[0] == 5
#     assert landmark.shape[1] == 2
#     tform = trans.SimilarityTransform()
#
#     tform.estimate(landmark, src)
#     M = tform.params[0:2, :]
#     img = cv2.warpAffine(
#         rimg, M, (image_size[1], image_size[0]), borderValue=0.0)
#     return img


def invoke_inspector(input_path, fig, output_dir, ignore_dir_pattern, ignore_file_pattern, requirements,
                     call_list, control_flow, directory_tree, software_invocation):
    dir_info = {}
    # retrieve readme text at the root level (if any)
    readme = ""
    try:
        with open(os.path.join(input_path, "README.md")) as readme_file:
            readme = readme_file.read()
    except:
        print("Readme not found at root level")
    for subdir, dirs, files in os.walk(input_path):

        for ignore_d in ignore_dir_pattern:
            dirs[:] = [d for d in dirs if not d.startswith(ignore_d)]
        for ignore_f in ignore_file_pattern:
            files[:] = [f for f in files if not f.startswith(ignore_f)]
        # print(files)
        for f in files:
            if ".py" in f and not f.endswith(".pyc"):
                try:
                    path = os.path.join(subdir, f)
                    out_dir = output_dir + "/" + os.path.basename(subdir)
                    cf_dir, json_dir = create_output_dirs(out_dir, control_flow)
                    code_info = CodeInspection(path, cf_dir, json_dir, fig, control_flow)
                    if out_dir not in dir_info:
                        dir_info[out_dir] = [code_info.fileJson[0]]
                    else:
                        dir_info[out_dir].append(code_info.fileJson[0])
                except:
                    print("Error when processing " + f + ": ", sys.exc_info()[0])
                    continue

    # Generate the call list of the Dir
    call_list_data = call_list_dir(dir_info)
    pruned_call_list_data = prune_json(call_list_data)
    if call_list:
        call_file_html = output_dir + "/call_graph.html"
        generate_output_html(pruned_call_list_data, call_file_html)
        call_json_file = output_dir + "/call_graph.json"
        with open(call_json_file, 'w') as outfile:
            json.dump(pruned_call_list_data, outfile)
    # Note:1 for visualising the tree, nothing or 0 for not.
    if requirements:
        dir_info["requirements"] = extract_requirements(input_path)
    if directory_tree or software_invocation:
        directory_tree_info = extract_directory_tree(input_path, ignore_dir_pattern, ignore_file_pattern, 1)
        if directory_tree:
            dir_info["directory_tree"] = directory_tree_info
        if software_invocation:
            # software invocation has both tests and regular invocation info.
            # Tests are separated in new category
            all_soft_invocation_info_list = extract_software_invocation(dir_info, directory_tree_info, input_path,
                                                                        call_list_data, readme)
            test_info_list = []
            soft_invocation_info_list = []
            for soft_info in all_soft_invocation_info_list:
                if "test" in soft_info["type"]:
                    test_info_list.append(soft_info)
                else:
                    soft_invocation_info_list.append(soft_info)
            dir_info["tests"] = test_info_list
            dir_info["software_invocation"] = soft_invocation_info_list
            # Order and rank the software invocation files found

            # Extract the first for software type.
            dir_info["software_type"] = rank_software_invocation(soft_invocation_info_list)
    return dir_info


if __name__ == '__main__':
    unittest.main()
