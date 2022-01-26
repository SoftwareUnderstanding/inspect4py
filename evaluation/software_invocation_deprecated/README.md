# Experiments and tests for determining the main command of a script/repo

# This folder is deprectated. See ../software_type for the newest evaluation results

This folder is for recording the experiments, discussions and test related to this research problem:

Given a software component:

- how can it be run?
- is it a package? a library? a script? a service?
- What are the parameters? associated functions? way of doing requests?

The file execution_commands_python describes examples of scripts, packages, libraries and services in python.

## Selection criteria:

These repositories were selected one or various of the following reasons:
- They were available from oour previous corpus in SOMEF.
- They are a reperesentative sample of the current practices by the community
- They are adopted, to a certain extent.
- They are Research Software, as well as Software in Research.
- They have been recommended in one of the awesome lists.

## Header meaning in evaluation summary

- `date`: Date when the evaluation was run
- `#repositories`: Number of repositories that were present in the evaluation report
- `#entries`: Number of entries in those repositories (a repo may be of more than one type, e.g., script and library)
- `#acc_repo`: Accuracy per repository. That is, if we get at least one type correctly from the repository.
- `#acc_entity`: Accuracy per number of entities.
- `#error_repos`: Titles of the repositories that produced an error (for inspection)
