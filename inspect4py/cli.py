import json
import tokenize
import types
import builtins
import click
from docstring_parser import parse as doc_parse

from inspect4py import __version__
from inspect4py.staticfg import builder
from inspect4py.utils import *

"""
Code Inspector
This class parses a file or files within directory
(and its subdirectories) to extract all the relevant information,
such as documentation, classes (and their methods), functions, etc.
To extract information from docstrings, we have started with the codes
documented.
This script requires `ast`, and `docsting_parse`
be installed within the Python environment you are running 
this script in.
"""

builtin_function_names = [name for name, obj in vars(builtins).items()
                          if isinstance(obj, types.BuiltinFunctionType)]


class CodeInspection:
    def __init__(self, path, out_control_flow_path, out_json_path, control_flow, abstract_syntax_tree, source_code):
        """ init method initializes the Code_Inspection object
        :param self self: represent the instance of the class
        :param str path: the file to inspect
        :param str out_control_flow_path: the output directory to store the control flow information
        :param str out_json_path: the output directory to store the json file with features extracted from the ast tree.
        :param bool control_flow: boolean to indicate to generate the control flow
        :param bool abstract_syntax_tree: boolean to indicate to generate ast in json format
        :param bool source_code: boolean to indicate to generate source code of each ast node.
        """

        self.path = path
        self.out_json_path = out_json_path
        self.abstract_syntax_tree = abstract_syntax_tree
        self.source_code = source_code
        self.tree = self.parser_file()
        if self.tree != "AST_ERROR":
            self.nodes = self.walk()
            self.class_init=self.find_classDef()
            self.fileInfo = self.inspect_file()
            self.depInfo = self.inspect_dependencies()
            self.funcsInfo, self.classesInfo = self.inspect_classes_funcs()
            self.bodyInfo = self.inspect_body()
            if control_flow:
                self.out_control_flow_path = out_control_flow_path
                self.controlFlowInfo = self.inspect_controlflow()
            else:
                self.controlFlowInfo = {}
            self.fileJson = self.file_json()
        else:
            self.fileJson = {}

    def find_classDef(self):
        classDef_nodes = [node for node in self.nodes if isinstance(node, ast.ClassDef)]
        class_init=[]
        for node in classDef_nodes:
            class_init.append(node.name)
        return class_init

    def parser_file(self):
        """ parse_file method parsers a file as an AST tree
        :param self self: represent the instance of the class
        :return ast.tree: the file as an ast tree
        """

        with tokenize.open(self.path) as f:
            try:
                return ast.parse(f.read(), filename=self.path)
            except:
                return "AST_ERROR"
    
    def walk(self):
        """
        recursivly traverses through self.tree and return all resultant nodes
        """
        stack = [self.tree]
        res = []
        while stack:
            node = stack.pop()
            res.append(node)
            # Stop traversing further when we meet function or class definitions
            if isinstance(node, ast.FunctionDef) or isinstance(node, ast.ClassDef):
                continue

            child_nodes = []
            for child in ast.iter_child_nodes(node):
                child.parent = node # Add parent reference to each child node
                child_nodes.append(child)
            
            # Maintain ast node order when traversing
            stack.extend(reversed(child_nodes))
        return res[1:] # The first node is self.tree, ignore it

    def inspect_file(self):
        """
        inspect_file method extracts the features at file level.
        Those features are path, fileNameBase, extension, docstring.
        The method support several levels of docstrings extraction,
        such as file's long, short a full descrition.
        :param self self: represent the instance of the class
        :return dictionary a dictionary with the file information extracted
        """
        file_info = {"path": os.path.abspath(self.path)}
        file_name = os.path.basename(self.path).split(".")
        file_info["fileNameBase"] = file_name[0]
        file_info["extension"] = file_name[1]
        ds_m = ast.get_docstring(self.tree)
        try:
            docstring = doc_parse(ds_m)
            file_info["doc"] = {}
            file_info["doc"]["long_description"] = docstring.long_description if docstring.long_description else {}
            file_info["doc"]["short_description"] = docstring.short_description if docstring.short_description else {}
            file_info["doc"]["full"] = ds_m if ds_m else {}
        except:
            file_info["doc"] = {}
        # fileInfo["doc"]["meta"]=docstring.meta if docstring.meta else {}
        return file_info

    def inspect_controlflow(self, format):
        """inspect_controlFlow using CFGBuilder
        :param self self: represent the instance of the class
        :param str format: represent the format to save the figure
        :return dictionary: a dictionary with the all information extracted (at file level)
        """
        control_info = {}
        try:
            ### Leaving Control Flow just with CFGBuilder
            cfg_visual = builder.CFGBuilder().build_from_file(self.fileInfo["fileNameBase"], self.path)
            cfg_path = self.out_control_flow_path + "/" + self.fileInfo["fileNameBase"]
            cfg_visual.build_visual(cfg_path, format=format, calls=False, show=False)
            control_info["cfg"] = cfg_path + "." + format
            # delete the second file generated by the cfg_visual (not needed!)
            os.remove(cfg_path)
        except:
            control_info["cfg"] = "ERROR"
        return control_info

    def inspect_classes_funcs(self):
        """ inspect classes and functions and detects all the functions, classes and their methods,
        and features.
        :param self self: represent the instance of the class
        :return dictionary: a dictionary with the all classes information extracted
        :return dictionary: a dictionary with the all functions information extracted
        """

        classes_info = self.inspect_classes()
        funcs_info, classes_info = self.inspect_functions(classes_info)
        funcs_info, classes_info = self.re_fill_call_list(classes_info, funcs_info)
        return funcs_info, classes_info

    def inspect_functions(self, classes_info):
        """ inspect_functions detects all the functions in a AST tree, and calls
        to _f_definitions method to extracts all the features at function level.
        :param self self: represent the instance of the class
        :param classes_info: information about the classes in the program
        :return dictionary: a dictionary with the all functions information extracted
        """

        functions_definitions = [node for node in self.nodes if isinstance(node, ast.FunctionDef)]
        function_definition_info = self._f_definitions(functions_definitions)
        # improving the list of calls
        functions_info = self._fill_call_name(function_definition_info, classes_info)

        # check for dynamic calls
        functions_info, classes_info = self._check_dynamic_calls(functions_definitions, functions_info,
                                                                 classes_info, type=1)
        return functions_info, classes_info

    def inspect_classes(self):
        """ inspect_classes detects all the classes and their methods,
         and extracts their features. It also calls to _f_definitions method
        to extract features at method level.
        The features extracted are name, docstring (this information is further analysed
        and classified into several categories), extends, start
        and end of the line and methods.
        :param self self: represent the instance of the class
        :return dictionary: a dictionary with the all classes information extracted
        """

        classes_definitions = [node for node in self.nodes if isinstance(node, ast.ClassDef)]
        classes_info = {}
        for c in classes_definitions:
            classes_info[c.name] = {}
            ds_c = ast.get_docstring(c)
            try:
                docstring = doc_parse(ds_c)
                classes_info[c.name]["doc"] = {}
                classes_info[c.name]["doc"][
                    "long_description"] = docstring.long_description if docstring.long_description else {}
                classes_info[c.name]["doc"][
                    "short_description"] = docstring.short_description if docstring.short_description else {}
                classes_info[c.name]["doc"]["full"] = ds_c if ds_c else {}
            except:
                classes_info[c.name]["doc"] = {}
            # classes_info[c.name]["doc"]["meta"]=docstring.meta if docstring.meta else {}
            try:
                classes_info[c.name]["extend"] = [b.id for b in c.bases]
            except:
                try:
                    extend = []
                    for b in c.bases:
                        if isinstance(b, ast.Call) and hasattr(b, 'value'):
                            extend.append(b.value.func.id)

                        # capturing extension type: module.import
                        elif b.value.id and b.attr:
                            extend.append(b.value.id + "." + b.attr)
                        elif b.value.id:
                            extend.append(b.value.id)
                        else:
                            extend.append("")
                    classes_info[c.name]["extend"] = extend
                    # classes_info[c.name]["extend"] = [
                    #    b.value.func.id if isinstance(b, ast.Call) and hasattr(b, 'value') else b.value.id if hasattr(b,
                    #                                                                                  'value') else ""
                    #    for b in c.bases]                                                             #'value') else ""
                except:
                    classes_info[c.name]["extend"] = []

            classes_info[c.name]["min_max_lineno"] = self._compute_interval(c)
            methods_definitions = [node for node in c.body if isinstance(node, ast.FunctionDef)]
            classes_info[c.name]["methods"] = self._f_definitions(methods_definitions)

        # improving the list of calls
        for c in classes_info:
            classes_info[c]["methods"] = self._fill_call_name(classes_info[c]["methods"], classes_info, c,
                                                              classes_info[c]["extend"])

        return classes_info

    def re_fill_call_list(self, classes_info, funcs_info):
        """ re fill call list,
        :param self self: represent the instance of the class
        :return dictionary: a dictionary with the all classes information extracted
        """

        # improving the list of calls
        for c in classes_info:
            classes_info[c]["methods"] = self._fill_call_name(classes_info[c]["methods"], classes_info, c,
                                                              classes_info[c]["extend"], type=2,
                                                              additional_info=funcs_info)
        classes_definitions = [node for node in self.nodes if isinstance(node, ast.ClassDef)]

        funcs_info, classes_info = self._check_dynamic_calls(classes_definitions, funcs_info, classes_info, type=2)
        return funcs_info, classes_info

    def inspect_body(self):
        call_nodes = [node for node in self.nodes if isinstance(node, ast.Call)]
        body_info = {"body": {}}
        body_store_vars = {}
        body_calls = []
        for node in call_nodes:
            body_name = self._get_func_name(node.func)
            if not body_name:
                continue
            body_calls.append(body_name)

            if isinstance(node.parent, ast.Assign):
                for target in node.parent.targets:
                    target_name = self._get_func_name(target)
                    body_store_vars[target_name] = body_name

            # skipping looking dynamic calls into imported moudules/libraries and built-in-functions
            if "." in body_name:
                check_body_name = body_name.split(".")[0]
            else:
                check_body_name = body_name
            if check_body_name in body_store_vars.keys():
                var_name = body_store_vars[check_body_name]
            else:
                var_name = ""

            skip = self._skip_dynamic_calls(self.funcsInfo, self.classesInfo, check_body_name, body_name,
                                            var_name)

            # new: dynamic functions
            if not skip:
                self._dynamic_calls(
                    node.args,
                    body_name,
                    self.funcsInfo,
                    self.classesInfo, body_store_vars)

        ### finding the index of init class ###
        index_remove=find_index_init(self.depInfo, body_calls, self.class_init)
        #######
        body_info["body"]["calls"] = body_calls
        body_info["body"]["store_vars_calls"] = body_store_vars
        body_info = self._fill_call_name(body_info, self.classesInfo, type=1, additional_info=self.funcsInfo)

        #### removing Class init from the calls  #####
        body_info["body"]["calls"]= update_list_calls(body_info["body"], index_remove)
        ###############

         

        if self.abstract_syntax_tree:
            body_info["body"]["ast"] = [ast_to_json(node) for node in call_nodes]
        if self.source_code:
            body_info["body"]["source_code"] = [ast_to_source_code(node) for node in call_nodes]
        return body_info

    def inspect_dependencies(self):
        """ inspect_dependencies method extracts the features at dependencies level.
        Those features are module , name, and alias.
        :param self self: represent the instance of the class
        :return dictionary: a dictionary with the all dependencies information extracted
        """

        dep_info = []
        for node in ast.iter_child_nodes(self.tree):
            if isinstance(node, ast.Import):
                module = []
            elif isinstance(node, ast.ImportFrom):
                try:
                    module = node.module
                    # module = node.module.split('.')
                except:
                    module = ''
            else:
                continue
            for n in node.names:
                if "*" in n.name:
                    functions, classes, type = list_functions_classes_from_module(module, self.path)
                    for f in functions:
                        current_dep = {"from_module": module,
                                       "import": f,
                                       "alias": n.asname,
                                       "type": type,
                                        "type_element": "function"}
                        dep_info.append(current_dep)
                    for f in classes:
                        current_dep = {"from_module": module,
                                       "import": f,
                                       "alias": n.asname,
                                       "type": type, 
                                        "type_element": "class"}
                        dep_info.append(current_dep)
                else:
                    import_name = n.name.split('.')[0]
                    type = type_module(module, import_name, self.path)
                    current_dep = {"from_module": module,
                                   "import": import_name,
                                   "alias": n.asname,
                                   "type": type,
                                    "type_element": "module"}
                    dep_info.append(current_dep)

        return dep_info

    def _ast_if_test(self):
        """
        Function that returns True if the file is a test
        """
        test_def = []
        for node in ast.iter_child_nodes(self.tree):
            if isinstance(node, ast.Assert):
                return True
            else:
                # look if the body of the node has asserts
                try:
                    for i in node.body:
                        if isinstance(i, ast.Assert):
                            return True
                except:
                    pass

        # Check if there are any functions with asserts.
        for f in self.funcsInfo.values():
            if any("assert" in call for call in f["calls"]):
                return True

        # Check if any methods of classes are asserts
        for cl in self.classesInfo.values():
            for method in cl["methods"].values():
                if any("assert" in call for call in method["calls"]):
                    return True

        # OPTION 2: searching the list of potential test in the imports
        test_dependencies = ('unittest', 'pytest', 'nose', 'nose2', 'doctest', 'testify', 'behave', 'lettuce')
        for dep in self.depInfo:
            imports = dep["import"]
            if isinstance(imports, list):
                for import_dep in imports:
                    if import_dep.lower() in test_dependencies:
                        return True
            else:
                if imports.lower() in test_dependencies:
                    return True

        # OPTION 3 (TO DO)
        # if the functions or classes imported belong to a test.
        # For example, there are cases where the final validation (assert) is done through an imported class

        # TO DO: assert should be the last statement of a test. If it then continues with other stuff, then it's
        # probably not a test.

        return False

    def _ast_if_main(self):
        """
        Method for getting if the file has a if __name__ == "__main__"
        and if it calls a method (e.g. main, version) or not.
        :param self self: represent the instance of the class
        :return main_info : dictionary with a flag stored in "main_flag" (1 if the if __name__ == main is found, 0 otherwise)
         and then "main_function" with the name of the function that is called.
        """

        if_main_definitions = [node for node in self.tree.body if isinstance(node, ast.If)]
        if_main_flag = 0
        if_main_func = ""
        main_info = {}

        for node in if_main_definitions:
            try:
                if node.test.comparators[0].s == "__main__":
                    if_main_flag = 1

                funcs_calls = [i.value.func for i in node.body if isinstance(i.value, ast.Call)]
                func_name_id = [self._get_func_name(func) for func in funcs_calls]

                # Note: Assigning just the first name in the list as the main function.
                if func_name_id:
                    if_main_func = self.fileInfo["fileNameBase"] + "." + func_name_id[0]
                    break
            except:
                pass

        main_info["main_flag"] = if_main_flag
        main_info["main_function"] = if_main_func
        if if_main_flag:
            main_info["type"] = "script"
        return main_info

    def file_json(self):
        """file_json method aggregates all the features previously
        extracted from a given file such as, functions, classes
        and dependencies levels into the same dictionary.

        It also writes this new dictionary to a json file.
        :param self self: represent the instance of the class
        :return dictionary: a dictionary with the all information extracted (at file level)
        """

        file_dict = {
            "file": self.fileInfo,
            "dependencies": self.depInfo,
            "classes": self.classesInfo,
            "functions": self.funcsInfo,
            "body": self.bodyInfo["body"],
            "controlflow": self.controlFlowInfo,
            "main_info": self._ast_if_main(),
            "is_test": self._ast_if_test()
        }

        json_file = self.out_json_path + "/" + self.fileInfo["fileNameBase"] + ".json"
        with open(json_file, 'w') as outfile:
            json.dump(prune_json(file_dict), outfile)
        return [file_dict, json_file]

    def _f_definitions(self, functions_definitions):
        """_f_definitions extracts the name, args, docstring
        returns, raises of a list of functions or a methods.
        Furthermore, it also extracts automatically several values
        from a docstring, such as long and short description, arguments'
        name, description, type, default values and if it they are optional
        or not.
        :param self self: represent the instance of the class
        :param list functions_definitions: represent a list with all functions or methods nodes
        :return dictionary: a dictionary with the all the information at function/method level
        """

        funcs_info = {}
        for f in functions_definitions:
            funcs_info[f.name] = {}
            ds_f = ast.get_docstring(f)
            try:
                docstring = doc_parse(ds_f)
                funcs_info[f.name]["doc"] = {}
                funcs_info[f.name]["doc"][
                    "long_description"] = docstring.long_description if docstring.long_description else {}
                funcs_info[f.name]["doc"][
                    "short_description"] = docstring.short_description if docstring.short_description else {}
                funcs_info[f.name]["doc"]["args"] = {}
                for i in docstring.params:
                    funcs_info[f.name]["doc"]["args"][i.arg_name] = {}
                    funcs_info[f.name]["doc"]["args"][i.arg_name]["description"] = i.description
                    funcs_info[f.name]["doc"]["args"][i.arg_name]["type_name"] = i.type_name
                    funcs_info[f.name]["doc"]["args"][i.arg_name]["is_optional"] = i.is_optional
                    funcs_info[f.name]["doc"]["args"][i.arg_name]["default"] = i.default
                if docstring.returns:
                    r = docstring.returns
                    funcs_info[f.name]["doc"]["returns"] = {}
                    funcs_info[f.name]["doc"]["returns"]["description"] = r.description
                    funcs_info[f.name]["doc"]["returns"]["type_name"] = r.type_name
                    funcs_info[f.name]["doc"]["returns"]["is_generator"] = r.is_generator
                    funcs_info[f.name]["doc"]["returns"]["return_name"] = r.return_name
                funcs_info[f.name]["doc"]["raises"] = {}
                for num, i in enumerate(docstring.raises):
                    funcs_info[f.name]["doc"]["raises"][num] = {}
                    funcs_info[f.name]["doc"]["raises"][num]["description"] = i.description
                    funcs_info[f.name]["doc"]["raises"][num]["type_name"] = i.type_name
            except:
                funcs_info[f.name]["doc"] = {}

            funcs_info[f.name]["args"] = []
            funcs_info[f.name]["annotated_arg_types"] = {}
            for a in f.args.args:
                funcs_info[f.name]["args"].append(a.arg)

                if a.annotation is not None:
                    funcs_info[f.name]["annotated_arg_types"][a.arg] = ast.unparse(a.annotation)
            if f.returns is not None:
                funcs_info[f.name]["annotated_return_type"] = ast.unparse(f.returns)

            rs = [node for node in ast.walk(f) if isinstance(node, (ast.Return,))]
            funcs_info[f.name]["returns"] = [self._get_ids(r.value) for r in rs]
            funcs_info[f.name]["min_max_lineno"] = self._compute_interval(f)
            funcs_calls = [node.func for node in ast.walk(f) if isinstance(node, ast.Call)]
            func_name_id = [self._get_func_name(func) for func in funcs_calls]

            # If we want to store all the calls, included the repeat ones, comment the next
            # line
            # func_name_id = list(dict.fromkeys(func_name_id))

            func_name_id = [f_x for f_x in func_name_id if f_x is not None]

            ### finding the index of init class ###
            index_remove=find_index_init(self.depInfo, func_name_id, self.class_init)
            funcs_info[f.name]["calls"] = func_name_id

            funcs_assigns = [node for node in ast.walk(f) if isinstance(node, ast.Assign)]
            funcs_store_vars = {}
            for f_as in funcs_assigns:
                if isinstance(f_as.value, ast.Name) and f_as.value.id == "self":
                    for target in f_as.targets:
                        target_name = self._get_func_name(target)
                        if target_name and f_as.value.id:
                            funcs_store_vars[target_name] = f_as.value.id

                elif isinstance(f_as.value, ast.Call):
                    func_name = self._get_func_name(f_as.value.func)
                    for target in f_as.targets:
                        target_name = self._get_func_name(target)
                        if target_name and func_name:
                            funcs_store_vars[target_name] = func_name
            funcs_info[f.name]["store_vars_calls"] = funcs_store_vars
            nested_definitions = [node for node in ast.walk(f) if isinstance(node, ast.FunctionDef)]
            for nested in nested_definitions:
                if f.name == nested.name:
                    nested_definitions.remove(nested)
            funcs_info[f.name]["calls"]= update_list_calls(funcs_info[f.name], index_remove)

            funcs_info[f.name]["functions"] = self._f_definitions(nested_definitions)

            # remove repeated calls in nested functions
            for n_f in funcs_info[f.name]["functions"]:
                if n_f in funcs_info[f.name]["calls"]:
                    remove_index = funcs_info[f.name]["calls"].index(n_f)
                    del funcs_info[f.name]["calls"][remove_index + 1:]

            for n_f in funcs_info[f.name]["functions"].copy():
                for n_f_2 in funcs_info[f.name]["functions"].copy():
                    if n_f in funcs_info[f.name]["functions"][n_f_2]["functions"]:
                        funcs_info[f.name]["functions"].pop(n_f)
                        break
            
            if self.abstract_syntax_tree:
                funcs_info[f.name]["ast"] = ast_to_json(f)
            if self.source_code:
                funcs_info[f.name]["source_code"] = ast_to_source_code(f)

        return funcs_info

    def _skip_dynamic_calls(self, funcs_info, classes_info, check_name, name, var_name):
        skip = 0
        if name not in funcs_info.keys() and check_name not in funcs_info.keys() and var_name not in funcs_info.keys():
            if name not in classes_info and check_name not in classes_info.keys() and var_name not in classes_info.keys():
                skip = 1

        return skip

    def _check_dynamic_calls(self, functions_defintions, funcs_info, classes_info, type=1):
        # type 1- from functions; type 2 from classes
        for f in functions_defintions:
            funcs_calls = [node for node in ast.walk(f) if isinstance(node, ast.Call)]
            for node in funcs_calls:
                skip = 0
                func_name_id = self._get_func_name(node.func)

                # NEW: checking if func_name_id is not NONE
                if func_name_id:
                    if type == 1:
                        store_vars = funcs_info[f.name]["store_vars_calls"]
                    else:
                        store_vars = {}
                        # store_vars=classesInfo[f.name]["store_vars_calls"]

                    if "." in func_name_id:
                        check_func_name_id = func_name_id.split(".")[0]
                    else:
                        check_func_name_id = func_name_id

                    if check_func_name_id in store_vars.keys():
                        var_name = store_vars[check_func_name_id]
                    else:
                        var_name = ""

                    skip = self._skip_dynamic_calls(funcs_info, classes_info, check_func_name_id, func_name_id,
                                                    var_name)

                    if not skip:
                        self._dynamic_calls(
                            node.args, func_name_id, \
                            funcs_info, classes_info, store_vars)

        return funcs_info, classes_info

    def _dynamic_calls(self, f_args, f_name_id, funcs_info, classes_info, store_vars={}):
        # new: dynamic call
        # f_args --> arguments
        # f_name_id --> name of the funtion which has been called

        # The idea is to check each argument (inside f_args), to check
        # if it is a function/method

        if "." in f_name_id:
            f_name = f_name_id.split(".")[0]
            if "()" in f_name:
                f_name = f_name.split("()")[0]
            f_name_rest = f_name_id.split(".")[1]

            if f_name in store_vars.keys():
                f_name = store_vars[f_name]
        else:
            f_name = f_name_id
            f_name_rest = f_name_id

        f_arg_cont = 0
        for f_arg in f_args:
            # We obtain the name of each argument, and we call it call_name
            call_name = self._get_func_name(f_arg)
            found = 0
            if call_name:
                # 1st, I look if the call_name
                # matches with any of the functions (of the curent module)
                # , which are stored in funcsInfo
                if call_name in funcs_info.keys():
                    # add the real dynamic call
                    try:
                        funcs_info[f_name]["calls"].append(self.fileInfo["fileNameBase"] + "." + call_name)
                        found = 1
                        argument_name = funcs_info[f_name]["args"][f_arg_cont]
                        for call in funcs_info[f_name]["calls"]:
                            if call == argument_name:
                                funcs_info[f_name]["calls"].remove(call)
                    except:
                        try:
                            if f_name_rest in classes_info[f_name]["methods"]:
                                classes_info[f_name]["methods"][f_name_rest]["calls"].append(
                                    self.fileInfo["fileNameBase"] + "." + call_name)
                                found = 1
                                argument_name = classes_info[f_name]["methods"][f_name_rest]["args"][f_arg_cont + 1]
                                for call in classes_info[f_name]["methods"][f_name_rest]["calls"]:
                                    if call == argument_name:
                                        classes_info[f_name]["methods"][f_name_rest]["calls"].remove(call)
                        except:
                            print("Error when processing dependency-1: %s call name: %s" % (f_name, call_name))

                else:
                    # 2nd, check if we find it the call_name
                    # can be found at in the imports /from_module/alias
                    if "." in call_name:
                        module_call_name = call_name.split(".")[0]
                        rest_call_name = call_name.split(".")[1:]
                        rest_call_name = '.'.join(rest_call_name)
                    else:
                        module_call_name = call_name
                        rest_call_name = call_name
                    for dep in self.depInfo:
                        if dep["import"] == module_call_name:
                            if dep["from_module"]:
                                try:
                                    funcs_info[f_name]["calls"].append(dep["from_module"] + "." + call_name)
                                    found = 1
                                    argument_name = funcs_info[f_name]["args"][f_arg_cont]
                                    for call in funcs_info[f_name]["calls"]:
                                        if call == argument_name:
                                            funcs_info[f_name]["calls"].remove(call)
                                except:
                                    try:
                                        if f_name_rest in classes_info[f_name]["methods"]:
                                            classes_info[f_name]["methods"][f_name_rest]["calls"].append(
                                                dep["from_module"] + "." + call_name)
                                            found = 1
                                            argument_name = classes_info[f_name]["methods"][f_name_rest]["args"][
                                                f_arg_cont + 1]
                                            for call in classes_info[f_name]["methods"][f_name_rest]["calls"]:
                                                if call == argument_name:
                                                    classes_info[f_name]["methods"][f_name_rest]["calls"].remove(call)
                                    except:
                                        print("Error when processing dependency-2: %s call name: %s" % (
                                            f_name, call_name))
                            else:
                                try:
                                    funcs_info[f_name]["calls"].append(call_name)
                                    found = 1
                                    argument_name = funcs_info[f_name]["args"][f_arg_cont]
                                    for call in funcs_info[f_name]["calls"]:
                                        if call == argument_name:
                                            funcs_info[f_name]["calls"].remove(call)
                                except:
                                    try:
                                        if f_name_rest in classes_info[f_name]["methods"]:
                                            classes_info[f_name]["methods"][f_name_rest]["calls"].append(call_name)
                                            found = 1
                                            argument_name = classes_info[f_name]["methods"][f_name_rest]["args"][
                                                f_arg_cont + 1]
                                            for call in classes_info[f_name]["methods"][f_name_rest]["calls"]:
                                                if call == argument_name:
                                                    classes_info[f_name]["methods"][f_name_rest]["calls"].remove(call)
                                    except:
                                        print("Error when processing dependency-3: %s call name: %s" % (
                                            f_name, call_name))

                        elif dep["alias"]:
                            if dep["alias"] == module_call_name:
                                if dep["from_module"]:
                                    try:
                                        funcs_info[f_name]["calls"].append(dep["from_module"] + "." + dep["import"])
                                        found = 1
                                        argument_name = funcs_info[f_name]["args"][f_arg_cont]
                                        for call in funcs_info[f_name]["calls"]:
                                            if call == argument_name:
                                                funcs_info[f_name]["calls"].remove(call)
                                    except:
                                        try:
                                            if f_name_rest in classes_info[f_name]["methods"]:
                                                classes_info[f_name]["methods"][f_name_rest]["calls"].append(
                                                    dep["from_module"] + "." + dep["import"])
                                                found = 1
                                                argument_name = classes_info[f_name]["methods"][f_name_rest]["args"][
                                                    f_arg_cont + 1]
                                                for call in classes_info[f_name]["methods"][f_name_rest]["calls"]:
                                                    if call == argument_name:
                                                        classes_info[f_name]["methods"][f_name_rest]["calls"].remove(
                                                            call)
                                        except:
                                            print("Error when processing dependency-4: %s call name: %s" % (
                                                f_name, call_name))
                                else:
                                    try:
                                        funcs_info[f_name]["calls"].append(dep["import"] + "." + call_name)
                                        found = 1
                                        argument_name = funcs_info[f_name]["args"][f_arg_cont]
                                        for call in funcs_info[f_name]["calls"]:
                                            if call == argument_name:
                                                funcs_info[f_name]["calls"].remove(call)
                                    except:
                                        try:
                                            if f_name_rest in classes_info[f_name]["methods"]:
                                                classes_info[f_name]["methods"][f_name_rest]["calls"].append(
                                                    dep["import"] + "." + call_name)
                                                found = 1
                                                argument_name = classes_info[f_name]["methods"][f_name_rest]["args"][
                                                    f_arg_cont + 1]
                                                for call in classes_info[f_name]["methods"][f_name_rest]["calls"]:
                                                    if call == argument_name:
                                                        classes_info[f_name]["methods"][f_name_rest]["calls"].remove(
                                                            call)
                                        except:
                                            print("Error when processing dependency-5: %s call_name: %s" % (
                                                f_name, call_name))

                    if not found:
                        if module_call_name in store_vars.keys():
                            module_call_name = store_vars[module_call_name]

                        # check if the call name matches with a class and method.
                        if "()" in module_call_name:
                            module_call_name = module_call_name.split("()")[0]

                        if module_call_name in classes_info.keys():
                            if rest_call_name in classes_info[module_call_name]["methods"].keys():
                                try:
                                    funcs_info[f_name]["calls"].append(
                                        self.fileInfo["fileNameBase"] + "." + module_call_name + "." + rest_call_name)
                                    argument_name = funcs_info[f_name]["args"][f_arg_cont]
                                    for call in funcs_info[f_name]["calls"]:
                                        if call == argument_name:
                                            funcs_info[f_name]["calls"].remove(call)
                                except:
                                    if f_name_rest in classes_info[f_name]["methods"]:
                                        classes_info[f_name]["methods"][f_name_rest]["calls"].append(
                                            self.fileInfo[
                                                "fileNameBase"] + "." + module_call_name + "." + rest_call_name)
                                        found = 1
                                        argument_name = classes_info[f_name]["methods"][f_name_rest]["args"][
                                            f_arg_cont + 1]
                                        for call in classes_info[f_name]["methods"][f_name_rest]["calls"]:
                                            if call == argument_name:
                                                classes_info[f_name]["methods"][f_name_rest]["calls"].remove(call)

            if found:
                print("Added in funct/method %s , argument named %s, number of argument %s" % (
                f_name, call_name, f_arg_cont))
            f_arg_cont += 1

    def _get_func_name(self, func):
        func_name = None
        if isinstance(func, ast.Name):
            return func.id

        elif isinstance(func, ast.Attribute):
            attr = ""
            attr += func.attr
            module = func.value
            while isinstance(module, ast.Attribute):
                attr = module.attr + "." + attr
                module = module.value

            # the module is not longer an ast. Attribute
            # entering here in case the module is a Name
            if isinstance(module, ast.Name):
                try:
                    func_name = module.id + "." + attr
                except:
                    pass
                return func_name

            # entering here in case the module is a Call
            # recursively!
            elif isinstance(module, ast.Call):
                try:
                    func_name = self._get_func_name(module.func) + "()." + attr
                except:
                    pass
                return func_name

            # the module is a subscript
            # recursively!
            elif isinstance(module, ast.Subscript):
                # ast.Subscripts
                try:
                    func_name = self._get_func_name(module.value)
                    if not func_name:
                        func_name = "[]." + attr
                    else:
                        func_name = func_name + "[]." + attr
                except:
                    pass
                return func_name
            else:
                return func_name

    def _dfs(self, extend, rest_call_name, renamed, classes_info, renamed_calls):
        for ext in extend:
            if ext in classes_info:
                if rest_call_name in classes_info[ext]["methods"]:
                    renamed_calls.append(self.fileInfo["fileNameBase"] + "." + ext + "." + rest_call_name)
                    renamed = 1
                    return renamed
                else:
                    extend = classes_info[ext]["extend"]
                    renamed = self._dfs(extend, rest_call_name, renamed, classes_info, renamed_calls)
                    if renamed:
                        break
            elif hasattr(ext, rest_call_name):
                renamed_calls.append(ext + "." + rest_call_name)
                renamed = 1
                return renamed
            else:
                pass
            #    extend = classes_info[ext]["extend"]
            #    renamed = self._dfs(extend, rest_call_name, renamed, classes_info, renamed_calls)
            #    if renamed:
            #        break
        return renamed

    def _fill_call_name(self, function_definition_info, classes_info, class_name="", extend=[],
                        type=0, additional_info={}):
        """
        :param type: 1 represents body, 2 represents re_fill_call, 3 represents nested call
        """
        for funct in function_definition_info:
            renamed_calls = []
            f_store_vars = function_definition_info[funct]["store_vars_calls"]
            for call_name in function_definition_info[funct]["calls"]:
                if call_name:
                    renamed = 0
                    module_call_name = call_name.split(".")[0]
                    if "super()" not in module_call_name:
                        module_call_name = module_call_name.split("()")[0]
                    rest_call_name = call_name.split(".")[1:]
                    rest_call_name = '.'.join(rest_call_name)

                    # We have to change the name of the calls and modules if we have
                    # the module stored as a variable in store_vars_calls

                    for key, val in f_store_vars.items():
                        if module_call_name == key:
                            module_call_name = val
                            call_name = module_call_name + "." + rest_call_name
                            break

                    # check if we are calling to the constructor of a class
                    # in that case, add fileNameBase and __init__
                    if call_name in classes_info:
                        # renamed_calls.append(self.fileInfo["fileNameBase"] + "." + call_name + ".__init__")
                        renamed_calls.append(self.fileInfo["fileNameBase"] + "." + call_name)

                    # check if we are calling "self" or  the module is a variable containing "self"
                    elif "self" in module_call_name:
                        renamed_calls.append(self.fileInfo["fileNameBase"] + "." + class_name + "." + rest_call_name)

                    elif "super()" in module_call_name and extend:
                        # dealing with Multiple Inheritance
                        # implemented depth first search algorithm
                        renamed = self._dfs(extend, rest_call_name, renamed, classes_info, renamed_calls)
                        if not renamed:
                            renamed_calls.append(call_name)
                    else:
                        if rest_call_name:
                            rest_call_name = "." + rest_call_name
                        else:
                            rest_call_name = ""

                        for dep in self.depInfo:
                            if dep["import"] == module_call_name:
                                if dep["from_module"]:
                                    renamed = 1
                                    renamed_calls.append(dep["from_module"] + "." + call_name)
                                    break
                                else:
                                    renamed = 1
                                    renamed_calls.append(call_name)

                            elif dep["alias"]:
                                if dep["alias"] == module_call_name:
                                    if dep["from_module"]:
                                        renamed = 1
                                        renamed_calls.append(dep["from_module"] + "." + dep["import"] + rest_call_name)
                                        break
                                    else:
                                        renamed = 1
                                        renamed_calls.append(dep["import"] + rest_call_name)
                                        break
                                else:
                                    pass
                        if not renamed:
                            # checking if the function has been imported "from module import *"
                            for dep in self.depInfo:
                                if dep["import"] == call_name:
                                    if dep["from_module"]:
                                        renamed = 1
                                        renamed_calls.append(dep["from_module"] + "." + call_name)
                                        break
                                    else:
                                        pass
                                else:
                                    pass

                            if not renamed:
                                # check if the call is to a  method of the current class
                                if class_name != "" and type != 3:
                                    if call_name in classes_info[class_name]["methods"].keys() and type != 3:
                                        renamed = 1
                                        renamed_calls.append(
                                            self.fileInfo["fileNameBase"] + "." + class_name + "." + call_name)
                                        break

                                # check if the call is to a function of the current module
                                if not renamed and call_name in function_definition_info.keys() and type != 3:
                                    renamed = 1
                                    renamed_calls.append(self.fileInfo["fileNameBase"] + "." + call_name)

                                # if body or re_fill_class.
                                elif type != 0 and call_name in additional_info.keys():
                                    renamed = 1
                                    renamed_calls.append(self.fileInfo["fileNameBase"] + "." + call_name)
                                else:
                                    pass

                                if not renamed:
                                    # if not body
                                    if type != 1:
                                        for inter_f in function_definition_info:
                                            if call_name in function_definition_info[inter_f]["functions"].keys():
                                                # if we are in a nested call
                                                if type == 3:
                                                    for nested_f in additional_info:
                                                        if inter_f in additional_info[nested_f]["functions"].keys():
                                                            renamed = 1
                                                            if class_name:
                                                                renamed_calls.append(self.fileInfo[
                                                                                         "fileNameBase"] + "." + class_name
                                                                                     + "." + nested_f + "." + inter_f + "."
                                                                                     + call_name)
                                                                break
                                                            else:
                                                                renamed_calls.append(
                                                                    self.fileInfo[
                                                                        "fileNameBase"] + "." + nested_f + "." +
                                                                    inter_f + "." + call_name)
                                                                break
                                                # otherwise
                                                else:
                                                    renamed = 1
                                                    if class_name:
                                                        renamed_calls.append(self.fileInfo["fileNameBase"] +
                                                                             "." + class_name + "." + inter_f +
                                                                             "." + call_name)
                                                        break
                                                    else:
                                                        renamed_calls.append(
                                                            self.fileInfo[
                                                                "fileNameBase"] + "." + inter_f + "." + call_name)
                                                        break
                                            else:
                                                pass
                                    if not renamed:
                                        if module_call_name and rest_call_name and \
                                                self.fileInfo["fileNameBase"] not in call_name:
                                            rest_call_name = rest_call_name.split(".")[1]
                                            if module_call_name in classes_info and rest_call_name in \
                                                    classes_info[module_call_name]["methods"].keys():
                                                renamed = 1
                                                renamed_calls.append(
                                                    self.fileInfo["fileNameBase"] + "." + module_call_name
                                                    + "." + rest_call_name)
                                            elif module_call_name in classes_info:
                                                renamed = self._dfs(classes_info[module_call_name]["extend"],
                                                                    rest_call_name,
                                                                    renamed, classes_info, renamed_calls)
                                                # if renamed:
                                                #    renamed_calls.append(self.fileInfo["fileNameBase"] + "." + call_name)
                                                # else:
                                                #    pass
                                            else:
                                                renamed = 1
                                                renamed_calls.append(call_name)
                                        else:
                                            pass

                                        if not renamed:
                                            if "super" != call_name:
                                                renamed_calls.append(call_name)
                                            else:
                                                pass
            function_definition_info[funct]["calls"] = renamed_calls

            if "functions" in function_definition_info[funct]:
                function_definition_info[funct]["functions"] = self._fill_call_name(
                    function_definition_info[funct]["functions"],
                    classes_info, class_name, extend, type=3,
                    additional_info=function_definition_info)
        return function_definition_info

    def _get_ids(self, elt):
        """_get_ids extracts identifiers if present.
         If not return None
        :param self self: represent the instance of the class
        :param ast.node elt: AST node
        :return list: list of identifiers
        """
        ## Modification of the function
        ## to catch the source code, in case if what we return is not a variable.
        if isinstance(elt, (ast.Tuple,)):
            # For tuple or list get id of each item if item is a Name
            rd=[]
            for x in elt.elts:
                if isinstance(x, (ast.Name,)):
                    rd.append(x.id)
                else:
                    rd.append(ast.unparse(x))
            if len(rd) == 0:
                return ast.unparse(elt)
            else:
                return rd
        elif isinstance(elt, (ast.Name,)):
            return elt.id

        else:
            return ast.unparse(elt)

    def _compute_interval(self, node):
        """_compute_interval extract the lines (min and max)
         for a given class, function or method.
        :param self self: represent the instance of the class
        :param ast.node node: AST node
        :return set: min and max lines
        """
        min_lineno = node.lineno
        max_lineno = node.lineno
        for node in ast.walk(node):
            if hasattr(node, "lineno"):
                min_lineno = min(min_lineno, node.lineno)
                max_lineno = max(max_lineno, node.lineno)
        return {"min_lineno": min_lineno, "max_lineno": max_lineno + 1}

    def _formatFlow(self, s):
        """_formatFlow reformats the control flow output
        as a text.
        :param self self: represent the instance of the class
        :param cfg_graph s: control flow graph
        :return str: cfg formated as a text
        """

        result = ""
        shifts = []  # positions of opening '<'
        pos = 0  # symbol position in a line
        next_is_list = False

        def is_next_list(index, maxIndex, buf):
            if index == maxIndex:
                return False
            if buf[index + 1] == '<':
                return True
            if index < maxIndex - 1:
                if buf[index + 1] == '\n' and buf[index + 2] == '<':
                    return True
            return False

        max_index = len(s) - 1
        for index in range(len(s)):
            sym = s[index]
            if sym == "\n":
                last_shift = shifts[-1]
                result += sym + last_shift * " "
                pos = last_shift
                if index < max_index:
                    if s[index + 1] not in "<>":
                        result += " "
                        pos += 1
                continue
            if sym == "<":
                if not next_is_list:
                    shifts.append(pos)
                else:
                    next_is_list = False
                pos += 1
                result += sym
                continue
            if sym == ">":
                shift = shifts[-1]
                result += '\n'
                result += shift * " "
                pos = shift
                result += sym
                pos += 1
                if is_next_list(index, max_index, s):
                    next_is_list = True
                else:
                    del shifts[-1]
                    next_is_list = False
                continue
            result += sym
            pos += 1
        return result


def create_output_dirs(output_dir, control_flow):
    """create_output_dirs creates two subdirectories
       to save the results. ControlFlow to save the
       cfg information (txt and PNG) and JsonFiles to
       save the aggregated json file with all the information
       extracted per file.
       :param str output_dir: Output Directory in which the new subdirectories
                          will be created.
       :param bool control_flow: Boolean to indicate the generation of the control flow
       """

    if control_flow:
        control_flow_dir = os.path.abspath(output_dir) + "/control_flow"

        if not os.path.exists(control_flow_dir):
            print("Creating cf %s" % control_flow_dir)
            os.makedirs(control_flow_dir)
        else:
            pass
    else:
        control_flow_dir = ""

    json_dir = output_dir + "/json_files"

    if not os.path.exists(json_dir):
        print("Creating jsDir:%s" % json_dir)
        os.makedirs(json_dir)
    else:
        pass
    return control_flow_dir, json_dir


@click.command()
@click.version_option(__version__)
@click.option('-i', '--input_path', type=str, required=True, help="input path of the file or directory to inspect.")
@click.option('-o', '--output_dir', type=str, default="output_dir",
              help="output directory path to store results. If the directory does not exist, the tool will create it.")
@click.option('-ignore_dir', '--ignore_dir_pattern', multiple=True, default=[".", "__pycache__"],
              help="ignore directories starting with a certain pattern. This parameter can be provided multiple times "
                   "to ignore multiple directory patterns.")
@click.option('-ignore_file', '--ignore_file_pattern', multiple=True, default=[".", "__pycache__"],
              help="ignore files starting with a certain pattern. This parameter can be provided multiple times "
                   "to ignore multiple file patterns.")
@click.option('-r', '--requirements', type=bool, is_flag=True, help="find the requirements of the repository.")
@click.option('-html', '--html_output', type=bool, is_flag=True,
              help="generates an html file of the DirJson in the output directory.")
@click.option('-cl', '--call_list', type=bool, is_flag=True,
              help="generates the call list in a separate html file.")
@click.option('-cf', '--control_flow', type=bool, is_flag=True,
              help="generates the call graph for each file in the target repository.")
@click.option('-dt', '--directory_tree', type=bool, is_flag=True,
              help="captures the file directory tree from the root path of the target repository.")
@click.option('-si', '--software_invocation', type=bool, is_flag=True,
              help="generates which are the software invocation commands to run and test the target repository.")
@click.option('-ast', '--abstract_syntax_tree', type=bool, is_flag=True,
              help="generates abstract syntax tree in json format.")
@click.option('-sc', '--source_code', type=bool, is_flag=True,
              help="generates the source code of each ast node.")
@click.option('-ld', '--license_detection', type=bool, is_flag=True,
              help="detects the license of the target repository.")
@click.option('-rm', '--readme', type=bool, is_flag=True,
              help="extract all readme files in the target repository.")
@click.option('-md', '--metadata', type=bool, is_flag=True, 
              help="extract metadata of the target repository using Github API. (requires repository to have the .git folder)")
def main(input_path, output_dir, ignore_dir_pattern, ignore_file_pattern, requirements, html_output, call_list,
         control_flow, directory_tree, software_invocation, abstract_syntax_tree, source_code, license_detection, readme,
         metadata):
    if (not os.path.isfile(input_path)) and (not os.path.isdir(input_path)):
        print('The file or directory specified does not exist')
        sys.exit()

    if os.path.isfile(input_path):
        cf_dir, json_dir = create_output_dirs(output_dir, control_flow)
        code_info = CodeInspection(input_path, cf_dir, json_dir, control_flow, abstract_syntax_tree, source_code)

        # Generate the call list of a file
        call_list_data = call_list_file(code_info)
        if call_list:
            call_file_html = json_dir + "/CallGraph.html"
            pruned_call_list_data = prune_json(call_list_data)
            generate_output_html(pruned_call_list_data, call_file_html)
            call_json_file = json_dir + "/CallGraph.json"
            with open(call_json_file, 'w') as outfile:
                json.dump(pruned_call_list_data, outfile)
        if html_output:
            output_file_html = json_dir + "/FileInfo.html"
            f = open(code_info.fileJson[1])
            data = json.load(f)
            generate_output_html(data, output_file_html)

    else:
        dir_info = {}
        # retrieve readme text at the root level (if any)
        readme = ""
        try:
            with open(os.path.join(input_path, "README.md")) as readme_file:
                readme = readme_file.read()
        except:
            try:
                with open(os.path.join(input_path, "README.rst")) as readme_file:
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
                        relative_path = Path(subdir).relative_to(Path(input_path).parent)
                        out_dir = str(Path(output_dir) / relative_path)
                        cf_dir, json_dir = create_output_dirs(out_dir, control_flow)
                        code_info = CodeInspection(path, cf_dir, json_dir, control_flow, abstract_syntax_tree, source_code)
                        if code_info.fileJson:
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
                soft_invocation_info_list = rank_software_invocation(soft_invocation_info_list)
                # Extract the first for software type.
                if len(soft_invocation_info_list) > 0:
                    dir_info["software_type"] = soft_invocation_info_list[0]["type"]
                else:
                    dir_info["software_type"] = "not found"
        if license_detection:
            try:
                licenses_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "licenses")
                rank_list = detect_license(input_path, licenses_path)
                dir_info["detected_license"] = [{k: f"{v:.1%}"} for k, v in rank_list]
            except:
                pass
        if readme:
            dir_info["readme_files"] = extract_readme(input_path)
        if metadata:
            dir_info["metadata"] = get_github_metadata(input_path)
        json_file = output_dir + "/directory_info.json"
        pruned_json = prune_json(dir_info)
        with open(json_file, 'w') as outfile:
            json.dump(pruned_json, outfile)
        print_summary(dir_info)
        if html_output:
            output_file_html = output_dir + "/directory_info.html"
            generate_output_html(pruned_json, output_file_html)


if __name__ == "__main__":
    main()

