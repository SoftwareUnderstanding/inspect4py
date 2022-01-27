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

### Preliminaries

Make sure you have graphviz installed:

```
sudo apt-get install graphviz
```

### Python version
We have tested `inspect4py` in Python 3.7+. **Our recommended version is Python 3.7**.

**Support in Python 3.9**: We have detected that `cdmcfparser` has issues in Python 3.9+. Therefore **the `-cf` command is not guaranteed in Python 3.9**. All other commands have been tested successfully in Python 3.9+.

### Operative System
We have tested `inspect4py` in Unix and MacOs.

### Installation from pypi
`inspect4py` is [available in pypi!](https://pypi.org/project/inspect4py/) Just install it like a regular package:

```
pip install inspect4py
```

You are done!

### Installation from code

Prepare a virtual Python3 enviroment, `cd` into the `inspect4py` folder and install the package as follows:

```
git clone https://github.com/SoftwareUnderstanding/inspect4py
cd inspect4py
pip install -e .
```

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

If you want to run the evaluations, do not forget to add `pandas` to the previous set

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

For more information about `inspect4py` execution options, please see the [usage section](https://inspect4py.readthedocs.io/en/latest/usage/).

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
