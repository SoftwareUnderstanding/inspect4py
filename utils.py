import ast
import os
import subprocess
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


def software_invocation(dir_info, input_path, call_list):
    """
    Method to detect the directory type of a software project.
    We distinguish four main types: script, package, library and service. Some can be more than one.
    :dir_info json file containing all the extracted information about the software repository
    :input_path path of the repository to analyze
    :call_list json file containing the list of calls per file and functions or methods.
    """
    software_invocation_info = []
    setup_files = ("setup.py", "setup.cfg")
    server_dependencies = ("flask", "flask_restful", "falcon", "falcon_app", "aiohttp", "bottle", "django", "fastapi",
                           "locust", "pyramid", "hug", "eve", "connexion")
    

    # Note: just doing a quick fix, so we ignore the ignore_pattern.
    #ignore_pattern = ("test", "debug")
    ignore_pattern=()
    # Note: other server dependencies are missing here. More testing is needed.
    flag_package_library = 0
    for directory in dir_info["directory_tree"]:
        for elem in dir_info["directory_tree"][directory]:
            if elem in setup_files:
                software_invocation_info.append(inspect_setup(input_path, elem))
                flag_package_library = 1
                break
                #### ATENTION!! - I AM COMMENTING THE RETURN TO ALLOW FURTHER EXPLORATION
                #return software_invocation_info

    # Looping across all mains
    # to decide if it is a service (main + server dep) or just a script (main without server dep)
    # Note: We are going to ignore all the directories and files that matches the ingore_pattern
    # to exclude tests, debugs and demos  
    main_files = []

    #new list to store the "mains that have been previously classified as "test". 
    test_files = []

    #new list to store files without mains
    no_main_files = []
    flag_service_main = 0
    for key in filter(lambda key: key not in "directory_tree", dir_info):
        result_ignore = [key for ip in ignore_pattern if ip in key]
        if not result_ignore:
            for elem in dir_info[key]:
                result_ignore = [elem["file"]["fileNameBase"] for ip in ignore_pattern if
                                 ip in elem["file"]["fileNameBase"]]
                if not result_ignore:
                    if elem["main_info"]["main_flag"]:
                        if elem["main_info"]["main_flag"]:
                            flag_main_service = 0
                            main_stored = 0
                            try:
                                flag_service, software_invocation_info = service_check(elem, result_ignore, software_invocation_info, server_dependencies)
                            except:
                                if elem["main_info"]["type"]!= "test":
                                     main_files.append(elem["file"]["path"])
                                else:
                                    test_files.append(elem["file"]["path"])
                                main_stored = 1

                            if flag_service:
                                flag_service_main = 1

                            if not flag_service and not main_stored:
                                if elem["main_info"]["type"]!= "test":
                                    main_files.append(elem["file"]["path"])
                                else:
                                    test_files.append(elem["file"]["path"])
                    else:
                        no_main_files.append(elem) 

    m_secondary=[0] * len(main_files)
    for m in range(0, len(main_files)):
        m_calls= find_file_calls(main_files[m], call_list)
        ## HERE I STORE WHICH OTHER MAIN FILES CALLS EACH "M" MAIN_FILE
        m_imports = extract_relations(main_files[m], m_calls, main_files, call_list)
        ## PRINT SANITY CHECK
        print("--- Sanity Check ---")
        print("Main File --%s-- has (direct/indirect) relation with these other Main Files --%s--" %(main_files[m], m_imports))
        
        for m_i in m_imports:
            m_secondary[main_files.index(m_i)]=1
  
    for m in range(0, len(main_files)):
        #### ONLY SELECT THE ONES THAT ARE PRINCIPALS - WE CAN CHANGE THAT LATER
        if not m_secondary[m]:
            soft_info = {"type": ["script with main"], "run": "python " + main_files[m] + " --help"}
            software_invocation_info.append(soft_info)

    ## ATENTION!!
    ## WE COULD COMMENT THIS - TO NOT INCLUDE IT IN THE TEST IN THE SOFTWARE INVOCATION
    ### STORING THE FILES THAT HAVE BEEN DETECTED AS "TESTS WITH MAIN"    
    for m in range(0, len(test_files)):
        soft_info = {"type": ["test"], "run": "python " + test_files[m] + " --help"}
        software_invocation_info.append(soft_info)

    ###### ATENTION: COMENTING IT TO LET IT CONTINUE - EVEN IF IT HAS FOUND A MAIN #####
    #if len(main_files) > 0:
    #    return software_invocation_info

    ##### ATENTION: ALLOWING IT TO EXPLORE IT FUTHER 
    # We are now go to try to find services in files without mains
    flag_service_no_main = 0
    for elem in no_main_files:
        flag_service, software_invocation_info = service_check(elem, result_ignore, software_invocation_info, server_dependencies)
        if flag_service:
            flag_service_no_main = 1

    ##### WE NOW ONLY ALLOWING TO EXPLORE MORE IF IT HAS NOT FIND: 1) PACKAGE/LIBRARY OR 2) SERVICES OR 3) MAINS
    if flag_service_main or flag_package_library or flag_service_no_main or len(main_files) > 0:
        return software_invocation_info

    # NOTE: OPTION 1
    # Note: Without ingore files and directories
    python_files = []
    for directory in dir_info["directory_tree"]:
        for elem in dir_info["directory_tree"][directory]:
            if ".py" in elem:
                python_files.append(os.path.abspath(input_path+"/"+ directory+"/"+elem))

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
    print("Finding the requirements with the pigar package for %s" % input_path)
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
    :pruned_json JSON to print out
    :output_file_html path where to write the HTML
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
        type = "internal"
    except:
        module = __import__(m)
        functions = dir(module)
        type = "external"
    return functions, type


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
        return "external"


def extract_call_functions(funcsInfo, body=0):
    call_list = {}
    if body:
        if funcsInfo["body"]["calls"]:
            call_list["local"] = funcsInfo["body"]["calls"]
    else:
        for funct in funcsInfo:
            if funcsInfo[funct]["calls"]:
                call_list[funct] = {}
                call_list[funct]["local"] = funcsInfo[funct]["calls"]
                if funcsInfo[funct]["functions"]:
                    call_list[funct]["nested"] = extract_call_functions(funcsInfo[funct]["functions"])
    return call_list


def extract_call_methods(classesInfo):
    call_list = {}
    for method in classesInfo:
        if classesInfo[method]["calls"]:
            call_list[method] = {}
            call_list[method]["local"] = classesInfo[method]["calls"]
            if classesInfo[method]["functions"]:
                call_list[method]["nested"] = extract_call_methods(classesInfo[method]["functions"])
    return call_list


def call_list_file(code_info):
    call_list = {}
    call_list["functions"] = extract_call_functions(code_info.funcsInfo)
    call_list["body"] = extract_call_functions(code_info.bodyInfo, body=1)
    for class_n in code_info.classesInfo:
        call_list[class_n] = extract_call_methods(code_info.classesInfo[class_n]["methods"])
    return call_list


def call_list_dir(dir_info):
    call_list = {}
    for dir in dir_info:
        call_list[dir] = {}
        for file_info in dir_info[dir]:
            file_path = file_info["file"]["path"]
            call_list[dir][file_path] = extract_call_functions(file_info["functions"])
            for class_n in file_info["classes"]:
                call_list[dir][file_path][class_n] = extract_call_methods(file_info["classes"][class_n]["methods"])
    return call_list


def find_file_calls(file_name, call_list):
    for dir in call_list:
        for elem in call_list[dir]:
            if elem in file_name:
                return call_list[dir][elem] 


def find_module_calls(module, call_list):
    for dir in call_list:
        for elem in call_list[dir]:
            if module in elem:
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
        #print("--> I found %s in %s" %(base, call))
        m_imports.append(file)
        return 1
    elif orig_base in call:
       return 0

    elif level < level_depth :
        m_calls_extern = {}
        module_base=call.split(".")[0]
        moudule_base = module_base +"."
        m_calls_extern = find_module_calls(module_base, call_list)
        ## Note: Here is when we increase the level of recursivity
        level += 1
        if m_calls_extern:
            for m_c in m_calls_extern:
                flag_found = extract_data(base, m_calls_extern[m_c], file, m_imports, 0, call_list, orig_base, level)
                if flag_found:
                    return 1
        return 0
    else:
        return 0

def extract_local_function(base, m_calls_local, file,  m_imports, flag_found, call_list, orig_base, level):
    for call in m_calls_local:
        flag_found= file_in_call(base, call, file, m_imports, call_list, orig_base, level)
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
          flag_found = extract_local_function(base, m_calls[elem], file, m_imports, flag_found, call_list, orig_base, level)
      elif elem == "nested":
          flag_found = extract_nested_function(base, m_calls[elem], file, m_imports, flag_found, call_list, orig_base, level)
      else:
          flag_found = extract_data(base, m_calls[elem], file, m_imports, flag_found, call_list, orig_base, level)
      if flag_found:
          return flag_found
  return flag_found 


# We will apply the DFS strategy later to find the external relationships.

def extract_relations(file_name, m_calls, main_files, call_list):
    m_imports=[]
    orig_base=os.path.basename(file_name)
    orig_base=os.path.splitext(orig_base)[0]
    orig_base = orig_base +"."
    for file in main_files:
        if file not in file_name:
            flag_found = 0
            base=os.path.basename(file)
            base=os.path.splitext(base)[0]
            base=base+"."
            for m_c in m_calls:
                level = 0
                flag_found = extract_data(base, m_calls[m_c], file, m_imports, flag_found, call_list, orig_base, level)
                if flag_found:
                    return m_imports
                            
    return m_imports


def service_check(elem, result_ignore, software_invocation_info, server_dependencies):
    flag_service = 0
    for dep in elem["dependencies"]:
        imports = dep["import"]
        flag_service, software_invocation_info= service_in_set(imports, server_dependencies, elem, software_invocation_info)
        if flag_service:
            return flag_service, software_invocation_info
        else: 
            modules = dep["from_module"]
            flag_service, software_invocation_info= service_in_set(modules, server_dependencies, elem, software_invocation_info)
            if flag_service:
                return flag_service, software_invocation_info
    return flag_service, software_invocation_info

def service_in_set(data, server_dependencies, elem, software_invocation_info):
    flag_service = 0
    if isinstance(data, list):
        for data_dep in data:
            if data_dep.lower() in server_dependencies:
                soft_info = {"type": ["service"], "run": elem["file"]["path"]}
                flag_service = 1
                if soft_info not in software_invocation_info:
                    software_invocation_info.append(soft_info)
    else:
         if data:
             if data.lower() in server_dependencies:
                 soft_info = {"type": ["service"], "run": elem["file"]["path"]}
                 flag_service = 1
                 if soft_info not in software_invocation_info:
                     software_invocation_info.append(soft_info)
    return flag_service, software_invocation_info
