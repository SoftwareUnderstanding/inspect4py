# code_inspector

Library to allow users inspect a software project folder (i.e., a directory and its subdirectories) and extract all the most relevant information, such as class, method and parameter documentation, classes (and their methods), functions, etc.

## Features

Given a folder with code, `code_inspector` will:

- Extract all classes in the code
- For each class, extract all its methods.
- For each class, extract all its imported modules and how each module is imported as.
- For each class and method, extract its documentation, including parameters, and accepted values.
- Record the control flow of each file.
- Requirement extraction from imported modules.
- Extraction of the main method to invoke the software (ongoing work).
- Extraction of the type of script or library that the code project is (e.g., a package, a service, a library, or a script). 

All metadata is extracted as a JSON file. See the [documentation](https://code-inspector.readthedocs.io/en/latest/output.html) for more details.


!!! warning
    `code_inspector` currently works **for Python projects only**. Some of its features (e.g., AST extraction) are only supported for Python 3.x projects. 

!!! info
    If you experience any issues when using code_inspector, please open an issue on our [GitHub repository](https://github.com/SoftwareUnderstanding/code_inspector/issues).