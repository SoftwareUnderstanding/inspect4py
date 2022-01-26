# inspect4py [![DOI](https://zenodo.org/badge/349160905.svg)](https://zenodo.org/badge/latestdoi/349160905)

<img src="docs/images/logo.png" alt="logo" width="200"/> 

Library to allow users inspect a software project folder (i.e., a directory and its subdirectories) and extract all the most relevant information, such as class, method and parameter documentation, classes (and their methods), functions, etc.

## Features:

Given a folder with code, `inspect4py` will:

- Extract all imported modules and how each module is imported as (i.e., whether they are internal or external).
- Extract all functions in the code, including their documentation, parameters, accepted values, and call list.
- Extract all classes in the code, with all their methods and respective documentation
- Extract the control flow of each file.
- Extract the hierarchy of directories and files.
- Extract the requirements used in the software project.
- Classify which files are tests
- Classify the main type of software project (script, package, library or service). Only one type is returned as main type (e.g., if a library has the option to be deployed as a service, `inspect4py` will return `Library` as its main type)
- Return a ranking of the different ways in which a a software component can be run, ordered by relevance.


All metadata is extracted as a JSON file.


Inspect4py currently works **only for Python 3 projects**.

## Background:

`inspect4py` uses [ASTs](https://en.wikipedia.org/wiki/Abstract_syntax_tree), more specifically
the [ast](https://docs.python.org/3/library/ast.html) module in Python, generating
a tree of objects (per file) whose classes all inherit from [ast.AST](https://docs.python.org/3/library/ast.html#ast.AST).

`inspect4py` parses each of the input file(s) as an AST tree, extracting the relevant information and storing it as a JSON file.  Furthermore, it also captures the control flow of each input file(s), by using another two libraries:

- [cdmcfparser](https://pypi.org/project/cdmcfparser/): The module provided functions can takes a file with a python code or a character buffer, parse it and provide back a hierarchical representation of the code in terms of fragments. Each fragment describes a portion of the input: a start point (line, column and absolute position) plus an end point (line, column and absolute position).

- [staticfg](inspect4py/staticfg): StatiCFG is a package that can be used to produce control flow graphs (CFGs) for Python 3 programs. The CFGs it generates can be easily visualised with graphviz and used for static analysis. We have a flag in the code (FLAG_PNG) to indicate if we want to generate this type of control flow graphs or not. **Note**: The original code of this package can be found [here](https://github.com/coetaur0/staticfg), which has been fixed it in our [repository](inspect4py/staticfg)  

We also use [docstring_parser](https://pypi.org/project/docstring-parser/), which has support for  ReST, Google, and Numpydoc-style docstrings. Some (basic) tests done using this library can be found at [here](./test_docstring_parser/).

Finally, we reuse [Pigar](https://github.com/damnever/pigar) for generating automatically the requirements of a given repository. This is an optional funcionality. In order to activate the argument (`-r`) has to be indicated when running inspect4py.  

## Install

### Python version
We have tested `inspect4py` in Python 3.7+. **Our recommended version is Python 3.7**.

**Support in Python 3.9**: We have detected that `cdmcfparser` has issues in Python 3.9+. Therefore **the `-cf` command is not guaranteed in Python 3.9**. All other commands have been tested successfully in Python 3.9+.

### Installation from code

First, make sure you have graphviz installed:

```
sudo apt-get install graphviz
```

Then, prepare a virtual Python3 enviroment, `cd` into the `inspect4py` folder and install the package as follows:

`pip install -e .`

You are done!

### Package dependencies: 
``` 
cdmcfparser
docstring_parser==0.7
astor
graphviz
click
pigar
setuptools==54.2.0
json2html
configparser
```

If you want to run the evaluations, do not forget to add `pandas` to the previous set.

### Installation through Docker

You need to have [Docker](https://docs.docker.com/get-started/) installed.

Next, clone the `inspect4py` repository:

```
git clone https://github.com/SoftwareUnderstanding/inspect4py/
```

Generate a Docker image for `inspect4py`:

```
docker build --tag inspect4py:1.0 .
```

Run the `inspect4py` image:

```
docker run -it --rm inspect4py:1.0 /bin/bash
```

Now you can run `inspect4py`:
```
root@e04792563e6a:/# inspect4py --help
```

For more information about `inspect4py` execution options, please see the section below (Execution).

Note that when running `inspect4py` with Docker, you will need to need to provide a path to the target repository to analyze. You can do this by:

1. Cloning the target repository. For example:

```
docker run -it --rm inspect4py:1.0 /bin/bash
# Docker image starts
root@e04792563e6a:/# git clone https://github.com/repo/id
root@e04792563e6a:/# inspect4py -i id 
```
2. Creating a [volume](https://docs.docker.com/storage/volumes/). For example, for mounting the $PWD folder: 

```
docker run -it -v -v $PWD:/out --rm inspect4py:1.0 /bin/bash
# Docker image starts
root@e04792563e6a:/# inspect4py -i /out/path/to/repo
```

<!--
Other useful commands when using Docker:
```
docker cp [OPTIONS] CONTAINER:SRC_PATH DEST_PATH|-
docker image rm -f inspect4py:1.0
```
-->

## Execution

The tool can be executed to inspect a file, or all the files of a given directory (and its subdirectories).
For example, it can be used to inspect all the python files of a given GitHub repository (that has been previously cloned locally).

The tool by default stores the results in the `OutputDir` directory, but users can specify their own directory name by using `-o` or `--output` flags.

And the tools allows users to specify if control flow figures will be generated or not. By default they wont be generated. To indicate the generation of control flow figures, users should use `-f` or `--fig`.  

<!--
```
inspect4py --input_path <FILE.py | DIRECTORY> [--fig , --output_dir "OutputDir", --ignore_dir_pattern "__", ignore_file_pattern "__" --requirements --html_output]
```
-->

For clarity, we have added a `help` command to explain each input parameter:

```
inspect4py --help

Usage: inspect4py [OPTIONS]

Options:
  --version                       Show the version and exit.
  -i, --input_path TEXT           input path of the file or directory to
                                  inspect.  [required]
  -f, --fig                       activate the control_flow figure generator.
  -o, --output_dir TEXT           output directory path to store results. If
                                  the directory does not exist, the tool will
                                  create it.
  -ignore_dir, --ignore_dir_pattern TEXT
                                  ignore directories starting with a certain
                                  pattern. This parameter can be provided
                                  multiple times to ignore multiple directory
                                  patterns.
  -ignore_file, --ignore_file_pattern TEXT
                                  ignore files starting with a certain
                                  pattern. This parameter can be provided
                                  multiple times to ignore multiple file
                                  patterns.
  -r, --requirements              find the requirements of the repository.
  -html, --html_output            generates an html file of the DirJson in the
                                  output directory.
  -cl, --call_list                generates the call list in a separate html
                                  file.
  -cf, --control_flow             generates the call graph for each file in a
                                  different directory.
  -dt, --directory_tree           captures the file directory tree from the
                                  root path of the target repository.
  -si, --software_invocation      generates which are the software
                                  invocation commands to run and test the
                                  target repository.
  --help                          Show this message and exit.
```

## Documentation

For additional documentation and examples, please have a look at our [online documentation](https://inspect4py.readthedocs.io/en/latest/)

## Acknowledgements

We would like to thank Laura Camacho, designer of the logo
