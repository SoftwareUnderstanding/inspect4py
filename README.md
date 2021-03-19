# code_inspector
Code_Inspector

## Dependencies

- Python 3
- Libraries:
  - ast
  - cdmcfparser
  - docstring_parser

## Execution

python code_inspector <FILE.py | DIRECTORY>

## Output

* Results are stored in **OutputDir** (created automatically)

* If the input is a **file**, the tool will create two folders:
	- JsonFiles directory: with a json file (with the name of the file + ".json") of the information extracted
	- ControlFile directory: with one or two (depending on the FLAG_PNG) Control Flow files will be created

* If the input is a **directory**, the tool will create two folders per **directory** and its **subdirectories** under **OutputDir**.
  Then, per directory will create a:
	- JsonFiles directory: with a Json file per file in the original directory
        - ControlFile directory: with one or two (depending of the FLAG_PNG) Control Flow files per file in the original directory

 Furthermore, a single JSON file with all the information found in given direcory is stored at:
    -  **OutputDir/DirectoryInfo.json**
