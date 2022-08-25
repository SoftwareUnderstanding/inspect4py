import os
import sys
import json
import pathlib

from inspect4py.cli import CodeInspection, create_output_dirs
from inspect4py.utils import call_list_dir, call_list_file, prune_json


def pycg_call_list(call_list: dict, root_dir: str):
    """
    Function to turn call list into pycg format
    :param call_list: original call list dictionary
    """
    call_graph = {}
    func_names = set()
    root_path = pathlib.Path(root_dir)

    def transform_funcs(
        func_list: dict, name_stack: list, call_graph: dict, func_names: set
    ):
        """
        Extracts all parent-children relations to call_graph while recording all
        function names appeared in func_names
        """
        for func_name, func_info in func_list.items():
            name_stack.append(func_name)

            current_name = ".".join(name_stack)
            call_graph[current_name] = func_info["local"]
            func_names.update(func_info["local"])

            if func_info.get("nested") is not None:
                transform_funcs(func_info["nested"], name_stack, call_graph, func_names)

            name_stack.pop()

    for dir_name, dir_info in call_list.items():
        for file_name, file_info in dir_info.items():
            # Strip the root dir and extension from each file path, and use . 
            # instead of / to connect each parent-child directory
            file_path = pathlib.Path(file_name)
            relative_filepath = file_path.relative_to(root_path).with_suffix("")
            pruned_filename = ".".join(relative_filepath.parts)

            func_names.add(pruned_filename)  # We also want to record each file name

            # extract body calls
            if file_info.get("body") is not None:
                transform_funcs(
                    {pruned_filename: file_info["body"]}, [], call_graph, func_names
                )

            # extract calls inside function definitions
            if file_info.get("functions") is not None:
                transform_funcs(
                    file_info["functions"], [pruned_filename], call_graph, func_names
                )

            # extract calls inside class method definitions
            if file_info.get("classes") is not None:
                for class_name, methods in file_info["classes"].items():
                    transform_funcs(
                        methods, [pruned_filename, class_name], call_graph, func_names
                    )

    res = dict.fromkeys(func_names, [])
    res.update(call_graph)

    return res

def main():
    if len(sys.argv) != 2:
        print("Usage: python pycg_convert.py <input_dir>")
        return
    input_path = sys.argv[1]
    output_dir = "./output_dir"
    control_flow = False
    fig = False
    ignore_dir_pattern = [".", "__pycache__"]
    ignore_file_pattern = [".", "__pycache__"]
    abstract_syntax_tree = False
    source_code = False

    if os.path.isfile(input_path):
        cf_dir, json_dir = create_output_dirs(output_dir, control_flow)
        code_info = CodeInspection(input_path, cf_dir, json_dir, fig, control_flow, abstract_syntax_tree, source_code)
        file_info = call_list_file(code_info)
        
        root_dir = os.path.dirname(input_path)
        call_list_data = {root_dir: {input_path: file_info}}
    else:
        dir_info = {}
        for subdir, dirs, files in os.walk(input_path):
            for ignore_d in ignore_dir_pattern:
                dirs[:] = [d for d in dirs if not d.startswith(ignore_d)]
            for ignore_f in ignore_file_pattern:
                files[:] = [f for f in files if not f.startswith(ignore_f)]
            for f in files:
                if ".py" in f and not f.endswith(".pyc"):
                    try:
                        path = os.path.join(subdir, f)
                        out_dir = output_dir + "/" + os.path.basename(subdir)
                        cf_dir, json_dir = create_output_dirs(out_dir, control_flow)
                        code_info = CodeInspection(path, cf_dir, json_dir, fig, control_flow, abstract_syntax_tree, source_code)
                        if out_dir not in dir_info:
                            dir_info[out_dir] = [code_info.fileJson[0]]
                        else:
                            dir_info[out_dir].append(code_info.fileJson[0])
                    except:
                        print("Error when processing " + f + ": ", sys.exc_info()[0])
                        continue
        root_dir = input_path
        call_list_data = call_list_dir(dir_info)

    pruned_call_list_data = prune_json(call_list_data)
    pycg_format_data = pycg_call_list(pruned_call_list_data, root_dir)
    call_json_file = output_dir + "/pycg_call_graph.json"
    with open(call_json_file, 'w') as outfile:
        json.dump(pycg_format_data, outfile)

if __name__ == "__main__":
    main()
