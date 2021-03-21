# code_inspector
Code_Inspector

## Dependencies

- Python 3
- Libraries:
  - ast
  - cdmcfparser
  - docstring_parser

## Execution

`python code_inspector.py <FILE.py | DIRECTORY>`

## Output

* Results are stored in **OutputDir** (created automatically)

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

  `python code_inspector.py code_inspector.py'


  Results are available here:

  ** [Json File](./OutputDir/JsonFiles) 
  ** [Control Flow](./OutputDir/ControlFlow)

  `> ls OuptuDir
   JsonFiles	ControlFlow
   > cd OutputDir
   > ls JsonFiles/
   code_inspector.json
   ls ControlFlow/
   code_inspector.png	code_inspector.txt`
