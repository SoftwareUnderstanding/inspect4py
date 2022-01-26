# Evaluation for determining the type and ordered ranking of software repositories

This folder is for recording the experiments, discussions and test related to this research problem:

Given a software component:

- how can it be run?
- What is its main type? is it a package? a library? a script? a service?
- If there are different ways of running the repository, which are they?

The file software_type_benchmark provides an annotated corpus of scripts, packages, libraries and services in python.

The file also returns the main files used to run the application, order by relevance. Relevance can be a little subjective,
but we have done the best to reflect what we believe the authors of the target repository considered the main methods of execution.
This is based on the readme, code comments, or structure of the repository. For example, if there is a demo script in the root
folder, that is mentioned in the readme, it is considered more relevant than an example script for part of the functionality in a sub-folder.
Similarly, the implementation of services is considered more relevant than simple scripts.

## Selection criteria:

These repositories were selected one or various of the following reasons:
- They are from [papers with code](https://paperswithcode.com/).
- They were available from our previous corpus in [SOMEF](https://github.com/KnowledgeCaptureAndDiscovery/somef/).
- They are a representative sample of the current practices by the community
- They are adopted tools, to a certain extent (i.e., great number of stars).
- They are Research Software, as well as Software in Research from research organizations.
- They have been recommended in one of the awesome lists.

## Header meaning in evaluation files

### software_type_benchmark.csv
Annotated benchmark, curated by hand.
- repository: repository id (in GitHub)
- annotator: Person who annotated the repository
- label: Correct software type.
- main_file_paths_1: most relevant files for repository execution.
- main_file_paths_2: files useful but not critical to run a repository.
- main_file_paths_3: files that are less relevant for running the tool.
- comments: Comments/discussion that occurred during annotation.

### evaluation_summary.csv
File with precision/recall metrics for each category type:
- date: Date when the experiment was carried out
- #repositories: Number of valid repositories analyzed.
- precision_package: Average precision for the package category
- recall_package: Average recall for the package category
- precision_library: Average precision for the library category
- recall_library: Average recall for the library category
- precision_service: Average precision for the service category
- recall_service: Average recall for the service category
- precision_script: Average precision for the script category
- recall_script: Average recall for the script category
- precision_avg: Average precision for all categories
- recall_avg: Average recall for all categories
- errors: Repositories where errors occurred (for debugging)

### evaluation_summary_scripts_ndcg.csv
File with the estimation of the ranking results, using normalized discounted cumultative gain
- date: Date when the experiment was carried out
- #repositories: Number of valid repositories analyzed.
- ndcg_avg: Normalized discounted cumulaltive gain (ranking evaluation)
- errors: Repositories where errors occurred (for debugging)

### evaluation_summary_scripts_precision_recall.csv:
File with the precision and recall of all the scripts considered "relevant" in the annotation corpus. **Note: this is ongoing work**.
- date: Date when the experiment was carried out.
- #repositories: Number of valid repositories analyzed.
- precision_avg: Average precision.
- recall_avg: Average recall.
- errors: Repositories where errors occurred (for debugging)

