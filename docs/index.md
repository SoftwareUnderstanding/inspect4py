# inspect4py

Library to allow users inspect a software project folder (i.e., a directory and its subdirectories) and extract all the most relevant information, such as class, method and parameter documentation, classes (and their methods), functions, etc.

## Features

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

All metadata is extracted as a JSON file. See the [documentation](https://inspect4py.readthedocs.io/en/latest/output.html) for more details.


!!! warning
    `inspect4py` currently works **for Python projects only**. Some of its features (e.g., AST extraction) are only supported for Python 3.x projects. 

!!! info
    If you experience any issues when using inspect4py, please open an issue on our [GitHub repository](https://github.com/SoftwareUnderstanding/inspect4py/issues).