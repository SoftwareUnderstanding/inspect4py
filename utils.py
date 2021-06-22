import ast
import json
import os
import subprocess
import tokenize
from pathlib import Path
from json2html import *

from parse_setup_files import inspect_setup
from structure_tree import DisplayablePath, get_directory_structure


def print_summary(json_dict):
    """
    This method prints a small summary of the classes and properties recognized during the analysis.
    At the moment this method is only invoked when a directory with multiple files is passed.
    """
    folders = 0
    files = 0
    dependencies = 0
    functions = 0
    classes = 0
    for key, value in json_dict.items():
        if "/" in key:
            folders += 1
        if isinstance(value, list):
            for element in value:
                files += 1
                if "dependencies" in element:
                    dependencies += len(element["dependencies"])
                if "functions" in element:
                    functions += len(element["functions"])
                if "classes" in element:
                    classes += len(element["classes"])
    print("Analysis completed")
    print("Total number of folders processed (root folder is considered a folder):", folders)
    print("Total number of files found: ", files)
    print("Total number of classes found: ", classes)
    print("Total number of dependencies found in those files", dependencies)
    print("Total number of functions parsed: ", functions)


def prune_json(json_dict):
    """
    Method that given a JSON object, removes all its empty fields.
    This method simplifies the resultant JSON.
    :param json_dict input JSON file to prune
    :return JSON file removing empty values
    """
    final_dict = {}
    if not (isinstance(json_dict, dict)):
        # Ensure the element provided is a dict
        return json_dict
    else:
        for a, b in json_dict.items():
            if b:
                if isinstance(b, dict):
                    aux_dict = prune_json(b)
                    if aux_dict:  # Remove empty dicts
                        final_dict[a] = aux_dict
                elif isinstance(b, list):
                    aux_list = list(filter(None, [prune_json(i) for i in b]))
                    if len(aux_list) > 0:  # Remove empty lists
                        final_dict[a] = aux_list
                else:
                    final_dict[a] = b
    return final_dict


def directory_tree(input_path, ignore_dirs, ignore_files, visual=0):
    """
    Method to obtain the directory tree of a repository.
    The ignored directories and files that were inputted are also ignored.
    :input_path path of the repo to
    """
    ignore_set = ['.git', '__pycache__', '.idea', '.pytest_cache']
    ignore_set = tuple(list(ignore_dirs) + list(ignore_files) + ignore_set)
    if visual:
        paths = DisplayablePath.make_tree(Path(input_path), criteria=lambda
            path: True if path.name not in ignore_set and not os.path.join("./", path.name).endswith(".pyc") else False)
        for path in paths:
            print(path.displayable())
    return get_directory_structure(input_path, ignore_set)


def software_invocation(dir_info, input_path):
    """
    Method to detect the directory type of a software project.
    We distinguish four main types: script, package, library and service.
    :dir_info json file containing all the extracted information about the software repositry
    :input_path path of the repository to analyze
    """
    software_invocation_info = []
    setup_files = ("setup.py", "setup.cfg")
    server_dependencies = ("Flask", "flask", "flask_restful")
    ignore_pattern = ("test", "demo", "debug")
    # ignore_pattern=()
    # Note: other server dependencies are missing here. More testing is needed.

    for directory in dir_info["directory_tree"]:
        for elem in dir_info["directory_tree"][directory]:
            if elem in setup_files:
                software_invocation_info.append(inspect_setup(input_path))
                return software_invocation_info

    # Looping across all mains
    # to decide if it is a service (main + flask) or just a script (main without flask)
    # Note: We are going to ignore all the directories and files that matches the ingore_pattern
    # to exclude tests, debugs and demos  
    main_files = []
    for key in filter(lambda key: key not in "directory_tree", dir_info):
        result_ignore = [key for ip in ignore_pattern if ip in key]
        if not result_ignore:
            for elem in dir_info[key]:
                result_ignore = [elem["file"]["fileNameBase"] for ip in ignore_pattern if
                                 ip in elem["file"]["fileNameBase"]]
                if not result_ignore:
                    if "main_info" in elem:
                        if elem["main_info"]["main_flag"]:
                            # print("------ DETECTED MAIN %s" %elem["file"]["fileNameBase"])
                            flag_service = 0
                            # Note:
                            # When we find a service in a main, it is very likely to be a service
                            try:
                                for dep in elem["dependencies"]:
                                    for import_dep in dep["import"]:
                                        if import_dep in server_dependencies:
                                            soft_info = {"type": ["service"], "app": elem["file"]["path"]}
                                            flag_service = 1
                                            software_invocation_info.append(soft_info)
                                            return software_invocation_info
                                    for from_mod_dep in dep["from_module"]:
                                        if from_mod_dep in server_dependencies:
                                            soft_info = {"type": ["service"], "app": elem["file"]["path"]}
                                            flag_service = 1
                                            software_invocation_info.append(soft_info)
                                            return software_invocation_info
                            except:
                                main_files.append(elem["file"]["path"])

                            if not flag_service:
                                main_files.append(elem["file"]["path"])

    # If we haven't found a service, but we have main(s)
    # it is very likely to be a service
    for m in range(0, len(main_files)):
        soft_info = {"type": ["script with main"], "run": "python " + main_files[m] + " --help"}
        software_invocation_info.append(soft_info)
    if len(main_files) > 0:
        return software_invocation_info

    # If we have not found a main, then we can try to find again if we have
    # a service
    # Note: We are going to ingore all the directories and files that matches the ingore_pattern
    # to exclude tests, debugs and demos  
    for key in filter(lambda key: key not in "directory_tree", dir_info):
        result_ignore = [key for ip in ignore_pattern if ip in key]
        if not result_ignore:
            for elem in dir_info[key]:
                result_ignore = [elem["file"]["fileNameBase"] for ip in ignore_pattern if
                                 ip in elem["file"]["fileNameBase"]]
                if not result_ignore:
                    try:
                        for dep in elem["dependencies"]:
                            for import_dep in dep["import"]:
                                if import_dep in server_dependencies:
                                    soft_info = {"type": ["service"], "app": elem["file"]["path"]}
                                    software_invocation_info.append(soft_info)
                                    return software_invocation_info
                            for from_mod_dep in dep["from_module"]:
                                if from_mod_dep in server_dependencies:
                                    soft_info = {"type":"service"}
                                    software_invocation_info.append(soft_info)
                                    return software_invocation_info
                    except:
                        pass

    # NOTE: OPTION 1
    # Note: Without ingore files and directories
    python_files = []
    for directory in dir_info["directory_tree"]:
        for elem in dir_info["directory_tree"][directory]:
            if ".py" in elem:
                python_files.append(elem)

    # NOTE: OPTION 2
    # Note: Ingoring all the directories and files that matches the ingore_pattern
    # to exclude tests, debugs and demos  
    # for directory in dir_info["directory_tree"]:
    #    result_ignore= [directory for ip in ignore_pattern if ip in directory]
    #    if not result_ignore:
    #        for elem in dir_info["directory_tree"][directory]:
    #            result_ignore= [elem for ip in ignore_pattern if ip in elem]
    #            if not result_ignore:
    #                if ".py" in elem:
    #                    python_files.append(elem)

    for f in range(0, len(python_files)):
        soft_info = {"type": ["script without main"], "run": "python " + python_files[f] + " --help"}
        software_invocation_info.append(soft_info)
    return software_invocation_info


def find_requirements(input_path):
    print("Finding the requirements with PIGAR for %s" % input_path)
    try:
        file_name = 'requirements_' + os.path.basename(input_path) + '.txt'

        # Attention: we can modify the output of pigar, if we use echo N.
        # Answering yes (echo y), we allow searching for PyPI
        # for the missing modules and filter some unnecessary modules.

        cmd = 'echo y | pigar -P ' + input_path + ' --without-referenced-comments -p ' + file_name
        # print("cmd: %s" %cmd)
        proc = subprocess.Popen(cmd.encode('utf-8'), shell=True, stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        req_dict = {}
        with open(file_name, "r") as file:
            lines = file.readlines()[1:]
        file.close()
        for line in lines:
            try:
                if line != "\n":
                    splitLine = line.split(" == ")
                    req_dict[splitLine[0]] = splitLine[1].split("\n")[0]
            except:
                pass
        # Note: Pigar requirement file is being deleted
        # in the future we might want to keep it (just commenting the line bellow)
        os.system('rm ' + file_name)
        return req_dict

    except:
        print("Error finding the requirements in" % input_path)


def generate_output_html(pruned_json, output_file_html):
    """
    Method to generate a simple HTML view of the obtained JSON.
    """
    html = json2html.convert(json=pruned_json)

    with open(output_file_html, "w") as ht:
        ht.write(html)


def top_level_functions(body):
    return (f for f in body if isinstance(f, ast.FunctionDef))


def parse_module(filename):
    with open(filename, "rt") as file:
        return ast.parse(file.read(), filename=filename)


def list_functions_from_module(m, path):
    functions = []
    
    try:
        # to open a module inside a directory
        m = m.replace(".", "/")
        repo_path = Path(path).parent.absolute()
        abs_repo_path = os.path.abspath(repo_path)
        file_module = abs_repo_path + "/" + m + ".py"
        tree = parse_module(file_module)
        for func in top_level_functions(tree.body):
            functions.append(func.name)
        type="internal"
    except:
        module = __import__(m)
        functions = dir(module)
        type="external"
    return functions, type

def type_module(m,i, path):
    repo_path = Path(path).parent.absolute()
    abs_repo_path = os.path.abspath(repo_path)
    if m:
       m = m.replace(".", "/")
       file_module = abs_repo_path + "/" + m + "/"+ i +".py"
    else:
       file_module = abs_repo_path + "/"+ i +".py"
    file_module_path=Path(file_module)
    if file_module_path.is_file():
        return "internal"
    else:
        return "external"


def extract_call_functions(funcsInfo):
    call_list={}
    for funct in funcsInfo:
        if funcsInfo[funct]["calls"]:
            call_list[funct] = {}
            call_list[funct]["local"] = funcsInfo[funct]["calls"]
            if funcsInfo[funct]["functions"]:
                 call_list[funct]["nested"]= extract_call_functions(funcsInfo[funct]["functions"])
    return call_list

def extract_call_methods(classesInfo):
    call_list={}
    for method in classesInfo:
        if classesInfo[method]["calls"]:
            call_list[method]={}
            call_list[method]["local"] = classesInfo[method]["calls"]
            if classesInfo[method]["functions"]:
                 call_list[method]["nested"]=extract_call_methods(classesInfo[method]["functions"])
    return call_list


def call_list_file(code_info):
    call_list = {}
    call_list=extract_call_functions(code_info.funcsInfo)
    for class_n in code_info.classesInfo:
         call_list[class_n] = extract_call_methods(code_info.classesInfo[class_n]["methods"])
    return call_list  

def call_list_dir(dir_info):
    call_list = {}
    for dir in dir_info:
        call_list[dir]={}
        for file_info in dir_info[dir]:
            file_path=file_info["file"]["path"]
            call_list[dir][file_path]={}
            for funct in file_info["functions"]:
                if file_info["functions"][funct]["calls"]:
                    call_list[dir][file_path][funct] = file_info["functions"][funct]["calls"]
            for class_n in  file_info["classes"]:
                call_list[dir][file_path][class_n] = {}
                for method in file_info["classes"][class_n]["methods"]:
                    if file_info["classes"][class_n]["methods"][method]["calls"]:
                        call_list[dir][file_path][class_n][method] = file_info["classes"][class_n]["methods"][method]["calls"]
    return call_list
