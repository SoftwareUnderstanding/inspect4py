# code_inspector

Library to allow users inspect a software project folder (i.e., a directory and its subdirectories) and extract all the most relevant information, such as class, method and parameter documentation, classes (and their methods), functions, etc.

## Features:

Given a folder with code, `code_inspector` will:

- Extract all classes in the code
- For each class, extract all its methods.
- For each class, extract all its imported modules and how each module is imported as.
- For each class and method, extract its documentation, including parameters, and accepted values.
- Record the control flow of each doe file.

All metadata is extracted as a JSON file.


Code inspector currently works **only for Python projects**.

## Dependencies:

It uses [AST](https://en.wikipedia.org/wiki/Abstract_syntax_tree), more specifically
the [ast](https://docs.python.org/3/library/ast.html) module in Python, generating
a tree of objects (per file) whose classes all inherit from [ast.AST](https://docs.python.org/3/library/ast.html#ast.AST).

code_inspector parsers each of the input file(s) as an ast tree, and walks across them, extracting
the relevant information, storing it as a JSON file.  Furthermore, it also captures the control
flow of each input file(s), by using another two libraries:

-[cdmcfparser](https://pypi.org/project/cdmcfparser/): The module provided functions can takes a file with a python code or a character buffer, parse it and provide back a hierarchical representation of the code in terms of fragments. Each fragment describes a portion of the input: a start point (line, column and absolute position) plus an end point (line, column and absolute position).

-[staticfg](./staticfg): StatiCFG is a package that can be used to produce control flow graphs (CFGs) for Python 3 programs. The CFGs it generates can be easily visualised with graphviz and used for static analysis. We have a flag in the code (FLAG_PNG) to indicate if we want to generate this type of control flow graphs or not. **Note**: The original code of this package can be found [here](https://github.com/coetaur0/staticfg), but given a bug in the package's source code, we forked it, and fixed it in our [repository](./staticfg)  

For parsing the docstrings, we use [docstring_parser](https://pypi.org/project/docstring-parser/), which has support for  ReST, Google, and Numpydoc-style docstrings. Some (basic) tests done using this library can be found at [here](./test_docstring_parser/).

It also usese [Pigar](https://github.com/damnever/pigar) for generating automatically the requirements of a given repository. This is an optional funcionality. In order to activate the argument (-r) has to be indicated when we run the code_inspector.  

## Install

### Installation from code

First, make sure you have graphviz installed:

```
sudo apt-get install graphviz
```

Then, prepare a virtual Python3 enviroment and install the required packages.

`pip install -r requirements.txt`

- Dependencies: 
  - cdmcfparser==2.3.2
  - docstring_parser==0.7
  - astor
  - graphviz
  - Click
  - setuptools == 54.2.0

### Installation through Docker

First, you will need to have [Docker](https://docs.docker.com/get-started/) installed.

Next, clone this repository:

```
git clone https://github.com/rosafilgueira/code_inspector/
```

Generate a Docker image for code_inspector:

```
docker build --tag inspector:1.0 .
```

Run code_inspector (you will have to copy the target data inside the image for analysis):

```
docker run -it --rm --entrypoint "/bin/bash" inspector:1.0
```

And then run `code_inspector` following the commands outlined in the sections below


Other useful commands when using Docker:
```
docker cp [OPTIONS] CONTAINER:SRC_PATH DEST_PATH|-
docker run -it --entrypoint "/bin/bash" inspector:1.0
docker image rm -f inspector:1.0
```

## Execution

The tool can be executed to inspect a file, or all the files of a given directory (and its subdirectories).
For example, it can be used to inspect all the python files of a given GitHub repository (that has been previously cloned locally).

The tool by default stores the results in the "OutputDir" directory, but users can specify their own directory name by using -o or --output flags.

And the tools allows users to specify if control flow figures will be generated or not. By default they wont be generated. To indicate the generation of control flow figures, users should use -f or --fig.  


```
python code_inspector.py --input_path <FILE.py | DIRECTORY> [--fig , --output_dir "OutputDir", --ignore_dir_pattern "__", ignore_file_pattern "__" --requirements]
```

For clarity, we have added the help option to explain each input parameters

```python code_inspector.py --help
Usage: code_inspector.py [OPTIONS]

Options:
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
  --help                          Show this message and exit.

```

## Outputs

* Results are stored by default inside the **OutputDir** directory, which is created automatically, if it is does not exits. Users have also the possibility to indicate their own directory name. 

* If the input is a **file**, the tool will create automatically two subdirectories inside **OuptuDir**:
	- **JsonFiles** directory: with a json file (with the name of the file + ".json") of the information extracted
	- **ControlFlow** directory: with one or two (depending on the FLAG_PNG) Control Flow files will be created

* If the input is a **directory**, the tool will create the previous directories (**JsonFiles** and **ControlFlow**) but per **directory** and its **subdirectories** instead, under **OutputDir**, storing all the information extracted per file found in each directory and/or subdirectory. The **OutputDir** directory will have the same subdirectory structure as the input directory given by the user. Furthermore, in order to facilitate the inspection of all the features extracted for a given directory (and its subdirectories), we have aggreagated all the previous json information in a **single json file** stored at **OutputDir/DirectoryInfo.json**.In other words, **OutputDir/DirectoryInfo.json**, represents all the features extracted of all files found in a given directory (and its subdirectories). 

### JSON FILE

* File features:
```
- file: 
	- path: <file_name>.py
        - fileNameBase: <file_name>
        - extension: py
        - doc:
               - long_description
               - short_description
               - full

```
* Dependencies features: 
```
- dependencies: (list of dependencies)
	-dep_<0>:
		- from_module
		        - 0: 
                        - ..: 
		- import 
			- 0:
			- ..:
		- alias
	-dep_<1>:
               	- ...
```
* Classes features:
```
- classes: (list of classes)
	-<class_name>:
		- doc:
			- long_description
			- short_description
			- full
                - extend
		- min_max_lineno:
			- min_lineno:
			- max_lineno:
		- methods (list of methods found within the class):
			-<method_name>:
				- doc:
					- long_description
					- short_description
					- args (list of arguments per method **documented**):
						- <name_arg>:
							- description
							- type_name
                                                        - is_optional
                                                        - default
						- <name_arg>:
							-  ...
					- returns: (information about the return *documented*)
						- description
						- type_name
                                		- is_generator
						- return_name
					- raises: (list of raises per method **documented**)
						- 0:
							- description
							- type_name
						- ...
				- args (list of arguments per method)
					- 0:
					- ..:
				- returns (list of returns found within the method)
					- 0:
					- ..:
				- min_max_lineno:
					- min_lineno:
					- max_lineno:
			-<method_name>:
				- ...
	-<class_name>:
		- ...				
```
   

* Function features:

```
- functions: (list of functions found within the class):
 	-<function_name>:
        	- doc:
                	- long_description
                        - short_description
                        - args (list of arguments per function **documented**):
                        	- <name_arg>:
                                	- description
                                        - type_name
                                        - is_optional
                                        - default
                                - <name_arg>:
                                        - ....
			- returns:
				- description
				- type_name
                                - is_generator
				- return_name
			- raises:(list of raises per function *documented**)
				- 0:
					- description
					- type_name
				- ...
                - args (list of arguments per function)
                	- 0:
                        - ..:
		- returns (list of returns found within the function)
			- 0:
			- ..:
                - min_max_lineno:
                	- min_lineno:
                        - max_lineno:
	-<function_name>:
                - ...
```
* ControlFlow features:
```
- controlflow:
	- cfg: Path of the cfg as a txt
	- png: Path of the cfg as a PNG

```
## Example

The easiest example is to run `code_inspector` against itself:

  `python code_inspector.py -i code_inspector.py -f`


Results of this run include a JSON file and a control flow file

If no output directory is specified, `code_inspector` will place the documentation in **OuptuDir**, including a JSON File and a control flow file for each code file found in the analyzed directory.

## Visualizing results

We include visualization tools to explore the results in an easy manner. Below we show some visualizations of the results for `code_inspector` code:

```
python code_visualization.py OutputDir/JsonFiles/<FILE>.json 
```
 

### Example 1: visualizing code_visualization.py

![visualization_code_visualization](docs/images/visual_code.png )

### Example 2: visualizing code_inspector.py

![visualization_code_inspector](docs/images/visual_code_inspector.png)
