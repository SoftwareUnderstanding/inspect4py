The tool can be executed to inspect a file, or all the files of a given directory (and its subdirectories).
For example, it can be used to inspect all the python files of a given GitHub repository (that has been previously cloned locally).

The tool by default stores the results in the "OutputDir" directory, but users can specify their own directory name by using -o or --output flags.

And the tools allows users to specify if control flow figures will be generated or not. By default they wont be generated. To indicate the generation of control flow figures, users should use -f or --fig.  


```
python code_inspector.py --input_path <FILE.py | DIRECTORY> [--fig , --output_dir "OutputDir", --ignore_dir_pattern "__", ignore_file_pattern "__" --requirements --html_output]
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
  -html, --html_output            generates an html file of the DirJson in the
                                  output directory.
  --help                          Show this message and exit.

```