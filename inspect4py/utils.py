import sys
import ast
import os
import re
import git
import requests
import subprocess
from pathlib import Path
import collections

from json2html import *
from bigcode_astgen.ast_generator import ASTGenerator

from inspect4py.parse_setup_files import inspect_setup
from inspect4py.structure_tree import DisplayablePath, get_directory_structure


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


def extract_directory_tree(input_path, ignore_dirs, ignore_files, visual=0):
    """
    Method to obtain the directory tree of a repository.
    The ignored directories and files that were inputted are also ignored.
    :input_path path of the repo to
    """
    ignore_set = ['.git', '__pycache__', '.idea', '.pytest_cache']
    ignore_set = tuple(list(ignore_dirs) + list(ignore_files) + ignore_set)
    if visual:
        paths = DisplayablePath.make_tree(Path(input_path), criteria=lambda
            path: True if path.name not in ignore_set and not os.path.join("../", path.name).endswith(".pyc") else False)
        for path in paths:
            print(path.displayable())
    return get_directory_structure(input_path, ignore_set)


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
            if a == "ast" and b:
                final_dict[a] = b # Avoid pruning AST fields
                continue
            if b or isinstance(b, bool):
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


def extract_requirements(input_path):
    print("Finding the requirements with the pigar package for %s" % input_path)
    try:
        file_name = 'requirements_' + os.path.basename(input_path) + '.txt'

        # Attention: we can modify the output of pigar, if we use echo N.
        # Answering yes (echo y), we allow searching for PyPI
        # for the missing modules and filter some unnecessary modules.


        #print(sys.version_info)   
        if sys.version_info[0] <=3 and sys.version_info[1]<=9:
            cmd = 'echo y | pigar -P ' + input_path + ' -p ' + file_name
        else:
            cmd = ' pigar generate ' + input_path + ' -f ' + file_name + ' --question-answer yes --auto-select'
       
        #print("-----> cmd: %s" %cmd)
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


def extract_software_invocation(dir_info, dir_tree_info, input_path, call_list, readme):
    """
    Method to detect the directory type of a software project. This method also detects tests
    We distinguish four main types: script, package, library and service. Some can be more than one.
    :dir_info json containing all the extracted information about the software repository
    :dir_tree_info json containing the directory information of the target repo
    :input_path path of the repository to analyze
    :call_list json file containing the list of calls per file and functions or methods.
    :readme content of the readme file of the project (if any)
    """

    software_invocation_info = []
    setup_files = ("setup.py", "setup.cfg")
    server_dependencies = ("flask", "flask_restful", "falcon", "falcon_app", "aiohttp", "bottle", "django", "fastapi",
                           "locust", "pyramid", "hug", "eve", "connexion")

    # Note: other server dependencies are missing here. More testing is needed.
    flag_package_library = 0
    for directory in dir_tree_info:
        for elem in setup_files:  # first check setup.py, then cfg
            if elem in dir_tree_info[directory]:
                # 1. Exploration for package or library
                software_invocation_info.append(inspect_setup(input_path, elem))
                flag_package_library = 1
                break
                # We continue exploration to make sure we continue exploring mains even after detecting this is a
                # library

    # Looping across all mains
    # to decide if it is a service (main + server dep) or just a script (main without server dep)
    main_files = []

    # new list to store the "mains that have been previously classified as "test".
    test_files_main = []
    test_files_no_main = []
    # new list to store files without mains
    body_only_files = []
    flag_service_main = 0
    for key in dir_info:  # filter (lambda key: key not in "directory_tree", dir_info):
        if key!="requirements" and key!="directory_tree": # Note: We need to filter out directory_tree
            for elem in dir_info[key]:
                if elem["main_info"]["main_flag"]:
                    flag_service_main = 0
                    flag_service = 0
                    main_stored = 0
                    if elem["is_test"]:
                        test_files_main.append(elem["file"]["path"])
                        main_stored = 1
                    else:
                        try:
                            # 2. Exploration for services in files with "mains"
                            flag_service, software_invocation_info = service_check(elem, software_invocation_info,
                                                                               server_dependencies, "main", readme)
                        except:
                            main_files.append(elem["file"]["path"])

                    if flag_service:
                        flag_service_main = 1

                    if not flag_service and not main_stored:
                        main_files.append(elem["file"]["path"])

                elif elem["is_test"]:
                    test_files_no_main.append(elem["file"]["path"])
                    # Filtering scripts with just body in software invocation
                elif elem['body']['calls']:
                    body_only_files.append(elem)

    m_secondary = [0] * len(main_files)
    flag_script_main = 0

    # this list (of lists) stores the mains that each main import
    import_mains = []
   
    # this list (of lists) stores the mains that each main is imported by
    imported_by = [None]*len(main_files)

    # 3. Exploration for main scripts
    for m in range(0, len(main_files)):
        m_calls = find_file_calls(main_files[m], call_list)
        # HERE I STORE WHICH OTHER MAIN FILES CALLS EACH "M" MAIN_FILE
        m_imports = extract_relations(main_files[m], m_calls, main_files, call_list)
      
        # storing those m_imports in the import_mains[m]
        import_mains.append(m_imports)
      
        for m_i in m_imports:
            m_secondary[main_files.index(m_i)] = 1

            if not imported_by[main_files.index(m_i)]:
                imported_by[main_files.index(m_i)] = []
            imported_by[main_files.index(m_i)].append(main_files[m])

    for m in range(0, len(main_files)):
        soft_info = {"type": "script", "run": "python " + main_files[m], "has_structure": "main",
                     "mentioned_in_readme": os.path.basename(os.path.normpath(main_files[m])) in readme,
                     "imports": import_mains[m], "imported_by": imported_by[m]}
        software_invocation_info.append(soft_info)
        flag_script_main = 1

    # tests with main.
    for t in range(0, len(test_files_main)):
        # Test files do not have help, they are usually run by themselves
        soft_info = {"type": "test", "run": "python " + test_files_main[t], "has_structure": "main",
                     "mentioned_in_readme": os.path.basename(os.path.normpath(test_files_main[t])) in readme}
        software_invocation_info.append(soft_info)
    # tests with no main.
    for t in range(0, len(test_files_no_main)):
        # Test files do not have help, they are usually run by themselves
        soft_info = {"type": "test", "run": "python " + test_files_no_main[t], "has_structure": "body",
                     "mentioned_in_readme": os.path.basename(os.path.normpath(test_files_no_main[t])) in readme}
        software_invocation_info.append(soft_info)

    flag_service_body = 0
    flag_script_body = 0
    for elem in body_only_files:
        # 4. Exploration for services in files with body 
        flag_service, software_invocation_info = service_check(elem, software_invocation_info,
                                                               server_dependencies, "body", readme)
        if flag_service:
            flag_service_body = 1

        # Only adding this information if we haven't not found libraries, packages, services or scripts with mains.
        # 5. Exploration for script without main in files with body 
        if not flag_service_main and not flag_service_body and not flag_package_library and not flag_script_main:
            soft_info = {"type": "script", "run": "python " + elem["file"]["path"], "has_structure": "body",
                         "mentioned_in_readme": elem["file"]["fileNameBase"] + "." + elem["file"][
                             "extension"] in readme}
            software_invocation_info.append(soft_info)
            flag_script_body = 1

    # Only adding this information if we haven't not found libraries, packages, services or scripts with mains
    # or bodies.
    # 6.  Exploration for script without main or body in files with body
    if not flag_script_body and not flag_service_main and not flag_service_body and not flag_package_library \
            and not flag_script_main:
        python_files = []
        for directory in dir_tree_info:
            for elem in dir_tree_info[directory]:
                if ".py" in elem:
                    python_files.append(os.path.abspath(input_path + "/" + directory + "/" + elem))

        for f in range(0, len(python_files)):
            soft_info = {"type": "script without main", "import": python_files[f], "has_structure": "without_body",
                         "mentioned_in_readme": os.path.basename(os.path.normpath(python_files[f])) in readme}
            software_invocation_info.append(soft_info)

    return software_invocation_info



def generate_output_html(pruned_json, output_file_html):
    """
    Method to generate a simple HTML view of the obtained JSON.
    :pruned_json JSON to print out
    :output_file_html path where to write the HTML
    """
    html = json2html.convert(json=pruned_json)

    with open(output_file_html, "w") as ht:
        ht.write(html)


def top_level_functions(body):
    return (f for f in body if isinstance(f, ast.FunctionDef))


def top_level_classes(body):
    return (c for c in body if isinstance(c, ast.ClassDef))


def parse_module(filename):
    with open(filename, "rt") as file:
        return ast.parse(file.read(), filename=filename)


def list_functions_classes_from_module(m, path):
    classes = []
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

        for cl in top_level_classes(tree.body):
            classes.append(cl.name)

        type = "internal"
    except:
        
        #module = __import__(m)
        #functions = dir(module)
        type = "external"
    return functions, classes, type


def type_module(m, i, path):
    repo_path = Path(path).parent.absolute()
    abs_repo_path = os.path.abspath(repo_path)
    if m:
        m = m.replace(".", "/")
        file_module = abs_repo_path + "/" + m + "/" + i + ".py"
    else:
        file_module = abs_repo_path + "/" + i + ".py"

    file_module_path = Path(file_module)
    if file_module_path.is_file():
        return "internal"
    else:
        if m:
           m = m.replace(".", "/")
           file_module = abs_repo_path + "/" + m + ".py"
           file_module_path = Path(file_module)
           if file_module_path.is_file():
               return "internal"
           else:
               file_module = abs_repo_path + "/" + m + "/main.py"
               file_module_path = Path(file_module)
               if file_module_path.is_file():
                   return "internal"
               else:
                   return "external"
        else:
            dir_module = abs_repo_path + "/" + i
            if os.path.exists(dir_module):
                   return "internal"
            else:
                return "external"


def extract_call_functions(funcs_info, body=0):
    call_list = {}
    if body:
        if funcs_info["body"]["calls"]:
            call_list["local"] = funcs_info["body"]["calls"]
    else:
        for funct in funcs_info:
            if funcs_info[funct]["calls"]:
                call_list[funct] = {}
                call_list[funct]["local"] = funcs_info[funct]["calls"]
                if funcs_info[funct]["functions"]:
                    call_list[funct]["nested"] = extract_call_functions(funcs_info[funct]["functions"])
    return call_list


def extract_call_methods(classes_info):
    call_list = {}
    for method in classes_info:
        if classes_info[method]["calls"]:
            call_list[method] = {}
            call_list[method]["local"] = classes_info[method]["calls"]
            if classes_info[method]["functions"]:
                call_list[method]["nested"] = extract_call_methods(classes_info[method]["functions"])
    return call_list


def call_list_file(code_info):
    call_list = {}
    call_list["functions"] = extract_call_functions(code_info.funcsInfo)
    call_list["body"] = extract_call_functions(code_info.bodyInfo, body=1)
    call_list["classes"] = {}
    for class_n in code_info.classesInfo:
        call_list["classes"][class_n] = extract_call_methods(code_info.classesInfo[class_n]["methods"])
    return call_list


def call_list_dir(dir_info):
    call_list = {}
    for dir in dir_info:
        call_list[dir] = {}
        for file_info in dir_info[dir]:
            file_path = file_info["file"]["path"]
            call_list[dir][file_path] = {}
            call_list[dir][file_path]["functions"] = extract_call_functions(file_info["functions"])
            call_list[dir][file_path]["body"] = extract_call_functions(file_info, body=1)
            call_list[dir][file_path]["classes"] = {}
            for class_n in file_info["classes"]:
                call_list[dir][file_path]["classes"][class_n] = extract_call_methods(file_info["classes"][class_n]["methods"])
    return call_list


def find_file_calls(file_name, call_list):
    for dir in call_list:
        for elem in call_list[dir]:
            if elem in file_name:
                return call_list[dir][elem]


def find_module_calls(module, call_list):
    for dir in call_list:
        for elem in call_list[dir]:
            if "/"+module+"." in elem:
                #print("---MODULE %s, elem %s, giving call_list[%s][%s]" %(module, elem, dir, elem))
                return call_list[dir][elem]

            # DFS algorithm - Allowing up to 2 levels of depth.


def file_in_call(base, call, file, m_imports, call_list, orig_base, level):
    ### NOTE: LEVEL is a parameter very important here!
    ### It allows us to track how deep we are inside the recursivity search.

    ### If we want to modify the depth of the recursity, we just need to change the level_depth.
    level_depth = 2

    ## For each call, we extract all its sub_calls (level 1), 
    ## and for each sub_call we extract all its sub_sub_calls (level 2)  
    #### 

    if base in call and m_imports.count(file) == 0 and orig_base not in call:
        m_imports.append(file)
        return 1
    elif orig_base in call:
        return 0

    elif level < level_depth and call!="":
        m_calls_extern = {}
        module_base = call.split(".")[0]
        module_base = module_base + "."
        m_calls_extern = find_module_calls(module_base, call_list)
        # Note: Here is when we increase the level of recursivity
        level += 1
        if m_calls_extern:
            for m_c in m_calls_extern:
                flag_found = extract_data(base, m_calls_extern[m_c], file, m_imports, 0, call_list, orig_base, level)
                if flag_found:
                    return 1
        return 0
    else:
        return 0


def extract_local_function(base, m_calls_local, file, m_imports, flag_found, call_list, orig_base, level):
    for call in m_calls_local:
        flag_found = file_in_call(base, call, file, m_imports, call_list, orig_base, level)
        if flag_found:
            return flag_found
    return flag_found


def extract_nested_function(base, m_calls_nested, file, m_imports, flag_found, call_list, orig_base, level):
    for call in m_calls_nested:
        flag_found = extract_data(base, m_calls_nested, file, m_imports, flag_found, call_list, orig_base, level)
        if flag_found:
            return flag_found
    return flag_found


def extract_data(base, m_calls, file, m_imports, flag_found, call_list, orig_base, level):
    for elem in m_calls:
        if elem == "local":
            flag_found = extract_local_function(base, m_calls[elem], file, m_imports, flag_found, call_list, orig_base,
                                                level)
        elif elem == "nested":
            flag_found = extract_nested_function(base, m_calls[elem], file, m_imports, flag_found, call_list, orig_base,
                                                 level)
        else:
            flag_found = extract_data(base, m_calls[elem], file, m_imports, flag_found, call_list, orig_base, level)
        if flag_found:
            return flag_found
    return flag_found


# We will apply the DFS strategy later to find the external relationships.

def extract_relations(file_name, m_calls, main_files, call_list):
    m_imports = []
    orig_base = os.path.basename(file_name)
    orig_base = os.path.splitext(orig_base)[0]
    orig_base = orig_base + "."
    for file in main_files:
        if file not in file_name:
            flag_found = 0
            base = os.path.basename(file)
            base = os.path.splitext(base)[0]
            base = base + "."
            for m_c in m_calls:
                level = 0
                flag_found = extract_data(base, m_calls[m_c], file, m_imports, flag_found, call_list, orig_base, level)
                if flag_found:
                    #return m_imports
                    break

    return m_imports


def service_check(elem, software_invocation_info, server_dependencies, has_structure, readme):
    flag_service = 0
    for dep in elem["dependencies"]:
        imports = dep["import"]
        flag_service, software_invocation_info = service_in_set(imports, server_dependencies, elem,
                                                                software_invocation_info, has_structure, readme)
        if flag_service:
            return flag_service, software_invocation_info
        else:
            modules = dep["from_module"]
            flag_service, software_invocation_info = service_in_set(modules, server_dependencies, elem,
                                                                    software_invocation_info, has_structure, readme)
            if flag_service:
                return flag_service, software_invocation_info
    return flag_service, software_invocation_info


def service_in_set(data, server_dependencies, elem, software_invocation_info, has_structure, readme):
    flag_service = 0
    if isinstance(data, list):
        for data_dep in data:
            if data_dep.lower() in server_dependencies:
                soft_info = {"type": "service", "run": "python " + elem["file"]["path"],
                             "has_structure": has_structure,
                             "mentioned_in_readme": elem["file"]["fileNameBase"] + "." + elem["file"][
                                 "extension"] in readme}
                flag_service = 1
                if soft_info not in software_invocation_info:
                    software_invocation_info.append(soft_info)
    else:
        if data:
            if data.lower() in server_dependencies:
                soft_info = {"type": "service", "run": "python " + elem["file"]["path"],
                             "has_structure": has_structure,
                             "mentioned_in_readme": elem["file"]["fileNameBase"] + "." + elem["file"][
                                 "extension"] in readme}
                flag_service = 1
                if soft_info not in software_invocation_info:
                    software_invocation_info.append(soft_info)
    return flag_service, software_invocation_info


def rank_software_invocation(soft_invocation_info_list):
    """
    Function to create a ranking over the different ways of executing a program.
    If two elements have the same position in the ranking, it means that there is no priority among them.
    Heuristic to order the invocation list is as follows, in decreasing order of prioritization:
        - If package or library is detected, this will be always first.
        - If something (script or service) is mentioned in the readme file, it is considered a priority.
        - Services are prioritized over scripts
        - Scripts with main are prioritized over script with body.
        - Scripts with body are prioritized over scripts with no body.
        TO DOs:
        - If a script imports other scripts (or service), it gets prioritized (TO DO when examples are available)
        - If several scripts are available, those at root level are prioritized (TO DO when examples are available)
    :param soft_invocation_info_list JSON list with the different ways to execute a program.
    """
    if len(soft_invocation_info_list) == 0:
        return soft_invocation_info_list
    # Calculate score for every entry in the list
    for entry in soft_invocation_info_list:
        score = 0
        if "library" in entry["type"] or "package" in entry["type"]:
            score += 100
        try:
            if entry["mentioned_in_readme"]:
                score += 10
        except:
            pass
        if "service" in entry["type"]:
            score += 5
        try:
            if "main" in entry["has_structure"]:
                score += 2
            if "body" in entry["has_structure"]:
                score += 1
        except:
            pass
        entry["ranking"] = score

    # Reorder vector and assign ranking
    soft_invocation_info_list.sort(key=lambda x: x["ranking"], reverse=True)

    # Replace score by number (but keep those with same score with the same ranking)
    position = 1
    previous_score = soft_invocation_info_list[0]["ranking"]
    for entry in soft_invocation_info_list:
        current_score = entry["ranking"]
        if previous_score > current_score:  # Ordered in descending order
            position += 1
            previous_score = current_score
        entry["ranking"] = position
    return soft_invocation_info_list

def ast_to_json(ast_obj):
    """
    Function to convert the AST object into JSON format.
    :param ast_obj: AST object
    """
    ast_generator = ASTGenerator("")
    ast_generator.tree = ast_obj
    return ast_generator.generate_ast()

def ast_to_source_code(ast_obj):
    """
    Function to convert the AST object into source code.
    :param ast_obj: AST object
    """
    return ast.unparse(ast_obj)


# Copied and modified from
# https://en.wikibooks.org/wiki/Algorithm_Implementation/Strings/Dice%27s_coefficient#Python
def dice_coefficient(a, b):
    """dice coefficient 2nt/(na + nb)."""
    if not len(a) or not len(b):
        return 0.0
    if len(a) == 1:
        a = a + u"."
    if len(b) == 1:
        b = b + u"."

    a_bigrams = {a[i : i + 2] for i in range(len(a) - 1)}
    b_bigrams = {b[i : i + 2] for i in range(len(b) - 1)}

    overlap = len(a_bigrams & b_bigrams)
    dice_coeff = overlap * 2.0 / (len(a_bigrams) + len(b_bigrams))
    return dice_coeff


def detect_license(input_path, licenses_path, threshold=0.9):
    """
    Function to detect the license of a file.
    :param input_path: Path of the repository to be analyzed.
    :param licenses_path: Path to the folder containing license templates.
    :param threshold: Threshold to consider a license as detected, 
           a float number between 0 and 1.
    """
    license_filenames = [
        "LICENSE",
        "LICENSE.txt",
        "LICENSE.md",
        "LICENSE.rst",
        "COPYING",
        "COPYING.txt",
        "COPYING.md",
        "COPYING.rst",
    ]
    license_file = None
    for filename in os.listdir(input_path):
        if filename in license_filenames:
            license_file = os.path.join(input_path, filename)
            break
    if license_file is None:
        return "No license file detected"

    with open(license_file, "r") as f:
        license_text = f.read()

    # Regex pattern for preprocessing license templates and extract spdx id
    pattern = re.compile(
        "(---\n.*(spdx-id: )(?P<id>.+?)\n.*---\n)(?P<template>.*)", re.DOTALL
    )
    rank_list = []
    for licen in os.listdir(licenses_path):
        with open(os.path.join(licenses_path, licen), "r") as f:
            parser = pattern.search(f.read())
            if parser is None:
                continue
            spdx_id = parser.group("id")
            license_template = parser.group("template")

        dice_coeff = dice_coefficient(license_text.strip(), license_template.strip())
        if dice_coeff > threshold:
            rank_list.append((spdx_id, dice_coeff))

    if rank_list:
        return sorted(rank_list, key=lambda t: t[1], reverse=True)

    return "License not recognised"


def extract_readme(input_path: str) -> dict:
    """
    Function to extract content of all readme file under the input directory.
    :param input_path: Path of the repository to be analyzed.
    """
    readme_files = {}
    for file in Path(input_path).rglob("README.*"):
        try:
            with open(file, 'r') as f:
                readme_files[str(file)] = f.read()
        except Exception as e:
            print(f"Error when opening {file}: {e}")

    return readme_files


def get_github_metadata(input_path: str) -> dict:
    """
    Function to extract metadata from the remote repository using Github api.
    It requires connectivity to the Github API and the local target repository 
    to have .git folder and a remote repository on Github.

    :param input_path: Path of the repository to be analyzed.
    """
    github_metadata = {}
    try:
        repo = git.Repo(input_path)
        remote_url = repo.remotes.origin.url

        # Extract owner and repo name from remote url
        api_param = re.search(r".+github.com[:/](?P<param>.+).git", remote_url).group("param")

        # Call Github API to get the metadata
        api_url = f"https://api.github.com/repos/{api_param}"
        response = requests.get(api_url)
        github_metadata = response.json()
    except git.InvalidGitRepositoryError as e:
        print(f"{input_path}.git not found or not valid: {e}")
    except git.NoSuchPathError as e:
        print(f"{input_path} does not exist: {e}")
    except requests.exceptions.RequestException as e:
        print(f"Error when accessing {api_url}: {e}")

    return github_metadata


def find_index_init(depInfo, calls, class_init):
    index_remove=[]
    for dep in depInfo:
        if dep["type_element"] == "class":
            if dep["import"] in calls:
                index_remove.append(calls.index(dep["import"]))
            elif dep["alias"] in calls:
                index_remove.append(calls.index(dep["alias"]))
    for i in class_init:
        if i in calls:
            index_remove.append(calls.index(i))
    return index_remove

def update_list_calls(info, index_remove):
    updated_calls=[]
    for i in range(0, len(info["calls"])):
        if i in index_remove:
            continue
        updated_calls.append(info["calls"][i])
    ### These lines are for removing duplicate calls 
    res = []
    for i in updated_calls :
        if i not in res:
            res.append(i)
    return res
