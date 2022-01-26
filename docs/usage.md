Inspect4py can be executed to inspect a file, or all the files of a given directory (and its subdirectories).
For example, it can be used to inspect all the python files of a given GitHub repository (that has been previously cloned locally).

The tool by default stores the results in the "OutputDir" directory, but users can specify their own directory name by using `-o` or `--output` flags.

And the tools allows users to specify if control flow figures will be generated or not. By default they wont be generated. To indicate the generation of control flow figures, users should use `-f` or `--fig`.  

```
inspect4py --input_path <FILE.py | DIRECTORY> [--fig , --output_dir "OutputDir", --ignore_dir_pattern "__", ignore_file_pattern "__" --requirements --html_output]
```


For clarity, we have added the help option to explain each input parameters

```inspect4py --help

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