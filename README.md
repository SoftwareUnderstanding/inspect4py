# code_inspector

The code_inspector allows the user to inspect a file or files within directory 
(and its subdirectories) and extract all the most relevant information, 
such as documentations, classes (and their methods), functions, etc.

It uses [AST](https://en.wikipedia.org/wiki/Abstract_syntax_tree), more specifically
the [ast](https://docs.python.org/3/library/ast.html) module in Python, generating
a tree of objects (per file) whose classes all inherit from [ast.AST](https://docs.python.org/3/library/ast.html#ast.AST).

code_inspector parsers each of the input file(s) as an ast tree, and walks across them, extracting
the relevant information, storing it as a JSON file.  Furthermore, it also captures the control
flow of each input file(s), by using another two libraries:

-[cdmcfparser](https://pypi.org/project/cdmcfparser/): The module provided functions can takes a file with a python code or a character buffer, parse it and provide back a hierarchical representation of the code in terms of fragments. Each fragment describes a portion of the input: a start point (line, column and absolute position) plus an end point (line, column and absolute position).

-[staticfg](./staticfg): StatiCFG is a package that can be used to produce control flow graphs (CFGs) for Python 3 programs. The CFGs it generates can be easily visualised with graphviz and used for static analysis. We have a flag in the code (FLAG_PNG) to indicate if we want to generate this type of control flow graphs or not. **Note**: The original code of this package can be found [here](https://github.com/coetaur0/staticfg), but given a bug in the package's source code, we forked it, and fixed it in our [repository](./staticfg)  

 

## Ideas for tool's name:
 - kodeXplain
 - sofexplain
 - kode_inspector

## Requirements

Prepare a virtual Python3 enviroment and install the required packages.

`pip install -r requirements.txt`

- Libraries:
  - cdmcfparser
  - docstring_parser

## Execution

The tool can be executed with a file o

`python code_inspector.py <FILE.py | DIRECTORY>`

## Outputs

* We store two types of results:
 - JSON file (per file in )

* Results are stored in **OutputDir** (created automatically). If **OutputDir** exits, the tool will delete it, and create it again, deleting all previous 
results stored in it. 

* If the input is a **file**, the tool will create two folders:
	- JsonFiles directory: with a json file (with the name of the file + ".json") of the information extracted
	- ControlFile directory: with one or two (depending on the FLAG_PNG) Control Flow files will be created

* If the input is a **directory**, the tool will create two folders per **directory** and its **subdirectories** under **OutputDir**.
  Then, per directory will create a:
	- JsonFiles directory: with a Json file per file in the original directory
        - ControlFile directory: with one or two (depending of the FLAG_PNG) Control Flow files per file in the original directory
  
  Furthermore, a **single JSON file** with all the previous json information is stored at **OutputDir/DirectoryInfo.json**

## Test

  We have executed our tool with itself.

  `python code_inspector.py code_inspector.py`


  Results of this test are available here:

* [Json File](./OutputDir/JsonFiles) 
* [Control Flow](./OutputDir/ControlFlow)

Notice how our tool, has automatically created two subdirectories inside **OuptuDir**, JsonFiles and ControlFlow.
Futhermore, out tool has saved the extracted information in a json file with the same NameBase as the file to inspect
(in this case **code_inspector.py**). And it also has saved the control flow (as a text and as a figure) in a similar maner, 
inside the ControlFlow directory (using also the same NameBase as the file to inspect). 

See bellow for more clarity:

```
  > ls OuptuDir
   JsonFiles	ControlFlow
  > cd OutputDir
  > ls JsonFiles/
   code_inspector.json
  > ls ControlFlow/
    code_inspector.png	code_inspector.txt
```
