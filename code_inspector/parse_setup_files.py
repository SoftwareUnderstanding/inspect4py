import os
import sys
import subprocess
import tempfile
from pathlib import Path
from unittest import mock
import configparser
import setuptools
import re

NON_AZ_REGEXP = re.compile('[^a-z]')


def normalize(word):
    """
    Normalize a word by converting it to lower-case and removing all
    characters that are not 'a',...,'z'.
    :param word: Word to normalize
    :type word: str or unicode
    :return: normalized word
    :rtype word: str or unicode
    """
    return re.sub(NON_AZ_REGEXP, '', word.lower())


def parse_setup_py(parent_dir):
    setup_info = {}
    setup_content = open(os.path.join(parent_dir, "setup.py")).read().split("\n")
    console_index = 0
    flag_console = 0
    name_index = 0
    flag_name = 0
    name = "UNKNOWN"
    for elem in setup_content:
        if 'name=' in elem:
            flag_name = 1
            break
        else:
            name_index += 1

    if flag_name:
        name = setup_content[name_index].split('=')[1].split(',')[0].replace('\'', '')
    single_line = 0
    for elem in setup_content:
        if 'console_scripts' in elem:
            flag_console = 1
            if ']' in elem:
                single_line = 1
            break
        else:
            console_index += 1
    if flag_console:
        cs_list = []
        setup_info["run"] = []

        if single_line:
            elem = setup_content[console_index]
            cs = elem.split("=")
            cs_string = cs[0].strip().replace('\'', '').split('["')[1]
            cs_list.append(normalize(cs_string))
            setup_info["installation"] = "pip install " + cs_string
            setup_info["run"].append(cs_string)
            setup_info["type"] = "package"

        else:
            for elem in setup_content[console_index+1:]:
                if ']' not in elem:
                    cs = elem.split("=")
                    cs_string = cs[0].strip().replace('\'', '')
                    setup_info["run"].append(cs)
                    cs_list.append(normalize(cs_string))
                else:
                    break
            setup_info["type"] = "package"
            setup_info["installation"] = "pip install " + name
        return setup_info
    else:
        setup_info["type"] = "library"
        setup_info["installation"] = "pip install " + name
        setup_info["run"] = "import " + name
        return setup_info


def inspect_setup_cfg(parent_dir, name, error=2):
    setup_info = {}
    setup_cfg = os.path.join(parent_dir, "setup.cfg")

    # checking if we have setup.cfg
    if Path(setup_cfg).is_file():
        parser = configparser.ConfigParser()
        with open("setup.cfg", "r") as f:
            parser.read_file(f)
        # extracting the name
        if not name:
            section = "metadata"
            if section in parser:
                metadata = dict(parser["metadata"])
                if "name" in metadata:
                    name = metadata["name"]
                else:
                    try:
                        name = subprocess.getoutput("python setup.py --name")
                    except:
                        name = "UNKNOWN"
            else:
                try:
                    name = subprocess.getoutput("python setup.py --name")
                except:
                    name = "UNKNOWN"
        name_norm = normalize(name)
        # extracting entry_points
        section = "entry_points"
        for s in parser:
            if section in s:
                data = dict(parser[s])
                if "console_scripts" in data:
                    console_scripts = data["console_scripts"].splitlines()
                    console_scripts.remove('')
                    setup_info["run"] = []
                    cs_list = []
                    for cs in console_scripts:
                        cs = cs.split("=")
                        cs_string = cs[0].rstrip()
                        #cs_run = cs[1].rstrip()
                        setup_info["run"].append(cs_string )
                        cs_list.append(normalize(cs_string))
                    setup_info["type"] = "package"
                    if name_norm not in cs_list:
                        cs_list_match_name = [i for i in cs_list if name_norm in i or i in name_norm]
                        if not cs_list_match_name:  
                            setup_info["type"] = "library"
                            setup_info["run"].append("import " + name)
                    return setup_info
        if error != 3:
            setup_info["type"] = "library"
            # In some cases, this fails silently
            if "Traceback (most recent call last)" not in name and "Warning:" not in name and "Failed " not in name:
                setup_info["installation"] = "pip install " + name
                setup_info["run"] = "import " + name
            return setup_info

        return setup_info
    else:
        # This is the last resource. We got here because an exception
        # or because we are not able to open setup.py and there is not setup.cfg
        # Classify it as package

        if error == 1:       
            setup_info = parse_setup_py(parent_dir)
            return setup_info

        try:
            if not name:
                setup_info["type"] = setuptools_method()
                name = subprocess.getoutput("python setup.py --name")
                if "Traceback (most recent call last)" not in name and "Warning:" not in name and "Failed " not in name:
                    name = name.split("\n")[-1]
                    if ".lib" in name:
                        name = name.split(".lib")[0]
                    setup_info["installation"] = "pip install " + name
                    setup_info["run"] = "import " + name
                else:
                    name = name.split("\n")[-1]
                    if ".lib" in name:
                        name = name.split(".lib")[0]
                    setup_info["installation"] = "pip install " + name
                return setup_info
        except:
            name = "UNKNOWN"
        #if error == 1:
        #    setup_info["type"] = "package"
        #    if "Traceback (most recent call last)" not in name and "Warning:" not in name and "Failed " not in name:
        #        setup_info["installation"] = "pip install " + name
        #        setup_info["run"] = name + " --help"

        if error == 2:
            setup_info["type"] = "library"
            if "Traceback (most recent call last)" not in name and "Warning:" not in name and "Failed " not in name:
                setup_info["installation"] = "pip install " + name
                setup_info["run"] = "import " + name
        return setup_info


def inspect_setup(parent_dir, elem):
    setup_info = {}
    abs_parent_dir = os.path.abspath(parent_dir)
    sys.path.insert(0, abs_parent_dir)
    current_dir = os.getcwd()
    os.chdir(abs_parent_dir)

    if elem in "setup.py":
        with tempfile.NamedTemporaryFile(prefix="setup_temp_", mode='w', dir=abs_parent_dir, suffix='.py') as temp_fh:
            with open(os.path.join(abs_parent_dir, "setup.py"), 'r') as setup_fh:
                temp_fh.write(setup_fh.read())
                temp_fh.flush()
            try:
                with mock.patch.object(setuptools, 'setup') as mock_setup:
                    module_name = os.path.basename(temp_fh.name).split(".")[0]
                    __import__(module_name)
            except:
                # mocking failed. Try to read setup.cfg or just parse setup.py.
                name = ""
                error = 1
                setup_info = inspect_setup_cfg(abs_parent_dir, name, error)
                os.chdir(current_dir)
                setup_info_aux = parse_setup_py(abs_parent_dir)
                # We return the one that finds the most useful ways of running.
                if len(setup_info_aux) > len(setup_info):
                    setup_info = setup_info_aux
                return setup_info
            finally:
                # need to blow away the pyc
                try:
                    os.remove("%sc" % temp_fh.name)
                except:
                    pass

            # successfully imported mock_setup
            if mock_setup.call_args_list:
                # we have call_args to inspect.
                # print("moc_setup.call_args_list works %s" % mock_setup.call_args_list)
                args, kwargs = mock_setup.call_args
                name = kwargs.get('name')
                entry_point = kwargs.get('entry_points')
                if not entry_point:
                    error = 2
                    setup_info = inspect_setup_cfg(abs_parent_dir, name,  error)
                    os.chdir(current_dir)
                    return setup_info
                else:
                    os.chdir(current_dir)
                    if 'console_scripts' in entry_point:
                        setup_info["run"] = []
                        cs_list = []
                        for cs in entry_point['console_scripts']:
                            cs = cs.split("=")
                            cs_string = cs[0].rstrip()
                            # cs_run = cs[1].rstrip()
                            setup_info["run"].append(cs_string)
                            cs_list.append(normalize(cs_string))
                        setup_info["type"] = "package"
                        name_norm = normalize(name)
                        if name_norm not in cs_list:
                            cs_list_match_name = [i for i in cs_list if name_norm in i or i in name_norm]
                            if not cs_list_match_name:
                                setup_info["run"].append("import " + name)
                                setup_info["type"] = "library"
                        setup_info["installation"] = "pip install " + name
                        return setup_info

                    else:
                        setup_info["type"] = "library"
                        setup_info["installation"] = "pip install " + name
                        setup_info["run"] = "import " + name
                        return setup_info

            else:
                # got an error with mock - lets check setup.cfg 
                setup_cfg = os.path.join(abs_parent_dir, "setup.cfg")
                if Path(setup_cfg).is_file():
                    name = ""
                    error = 3
                    setup_info = inspect_setup_cfg(abs_parent_dir, name, error)
                    if setup_info:
                        os.chdir(current_dir)
                        return setup_info
                    else:
                        setup_info = parse_setup_py(abs_parent_dir)
                        os.chdir(current_dir)
                        return setup_info
                else:
                    setup_info = parse_setup_py(abs_parent_dir)
                    os.chdir(current_dir)
                    return setup_info
    else:
        name = ""
        error = 1
        setup_info = inspect_setup_cfg(abs_parent_dir, name, error)
        os.chdir(current_dir)
        return setup_info


def setuptools_method():
    setuptools.setup = setup
    content = open('setup.py').read()
    if "entry_points" in content:
        return "package"
    else:
        return "library"


def setup(**kwargs):
    print(kwargs)
