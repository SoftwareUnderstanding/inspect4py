"""
Very simple class to test out the test_dir method.
Note: this assumes that the ../../../test_repos/ repo exist.

This file is deprecated. The run_software_type_evaluation.py is the most dated evaluation
"""
import csv
import os
import subprocess
import json
import pandas as pd
from datetime import datetime

# TODO: These should be configured separately, or set by input
repo_path = "../../../test_repos/"
benchmark_path = "../../evaluation/software_invocation/execution_commands_python_benchmark.csv"
# benchmark_path = "evaluation/execution_commands_python_benchmark_test.csv"
benchmark_summary = "../../evaluation/software_invocation/evaluation_summary.csv"


def extract_types_from_response(response_data):
    """
    This function extracts the list of types found by code_inspector from the response.
    :param response_data json response from code_inspector
    """
    types = []
    software_info = {}
    if "software_invocation" in response_data:
        software_info = response_data['software_invocation']
        for soft_entry in software_info:
            type_s = soft_entry["type"] # "type" is not a list anymore
            if type_s not in types:
                if "script" in type_s:  # we have annotated script with main and without main as script
                    types.append("script")
                else:
                    types.append(type_s)
    return types, software_info


# Main script
benchmark_df = pd.read_csv(benchmark_path)

if not os.path.isdir(repo_path):
    os.makedirs(repo_path)

# Download repos if they don't exist in the repo_path
for index, row in benchmark_df.iterrows():
    current_repo = "https://github.com/" + row["repository"]
    print("Downloading: " + row["repository"])
    cmd = 'cd ' + repo_path + ' && git clone ' + current_repo
    proc = subprocess.Popen(cmd.encode('utf-8'), shell=True, stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()

# Process all repos
num_correct_repo = 0
num_correct_entity = 0
num_error_repo = 0
num_error_entity = 0
num_analyses_repo = 0
num_analyses_entity = 0
repos_with_error = []
repos_with_error_entity = []

for dir_name in os.listdir(repo_path):
    print("######## Processing: " + dir_name) # repo_path
    cmd = 'inspect4py -i ' + repo_path + dir_name + " -o ../../output_dir/ -si"
    proc = subprocess.Popen(cmd.encode('utf-8'), shell=True, stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = proc.communicate()
    req_dict = {}
    if not os.path.exists("../../output_dir/directory_info.json"):
        print("Error when applying code_inspector to " + dir_name + str(stderr))
        num_error_repo += 1
        num_error_entity += 1
        repos_with_error.append(dir_name)
        repos_with_error_entity.append(dir_name)
        continue
    with open("../../output_dir/directory_info.json", "r") as file:
        data = json.load(file)
    file.close()
    # delete last DirInfo to avoid reading incorrect information in case of errors.
    os.remove("../../output_dir/directory_info.json")
    current_type = []
    # This will have to be changed if software_invocation JSON definition is changed
    if 'software_invocation' in data.keys() and data['software_invocation']:
        # print(dirname+" "+str(data['software_invocation']))
        # print(str(data['software_invocation']))
        current_type, software_inf = extract_types_from_response(data)

    flag = 0
    for index, row in benchmark_df.iterrows():
        if dir_name == row["repository"].split("/")[-1].strip():
            row_types = [x.strip() for x in row["type"].split("and")]
            print("ATTENTION DANI-ROSA Annotated types in CSV: --%s--- vs CODE INSPECTOR types --%s--" % (row_types, current_type))
            repo_correct = False
            print_err_entities = False
            for row_type in row_types:
                if row_type in current_type:
                    # If at least one is correct, then +1
                    repo_correct = True
                    num_correct_entity += 1
                else:
                    num_error_entity += 1
                    print_err_entities = True # tracked with a bool so we don't print several times.
                    print("## ERROR type for %s: infer type [%s] - real type [%s]" % (dir_name, current_type, row_type))
                    print("## ERROR TOTAL INFO INFERRED for %s - %s" % (dir_name, software_inf))
            if repo_correct:
                num_correct_repo += 1
            else:
                num_error_repo += 1
                repos_with_error.append(dir_name)
            if print_err_entities:
                repos_with_error_entity.append(dir_name)
            num_analyses_repo += 1
            num_analyses_entity += len(row_types)
            flag = 1
    if not flag:
        print("--> ATTENTION! %s NOT FOUND! " % dir_name)

# Create evaluation_summary.
write_header = False
if not os.path.exists(benchmark_summary):
    write_header = True

with open(benchmark_summary, 'a') as summary:
    writer = csv.writer(summary, delimiter=',')
    if write_header:
        writer.writerow(
            ['date', '#repositories', '#entities', 'acc_repo', 'acc_entity', 'error_repos', 'error_entities'])
    date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
    writer.writerow([date, num_analyses_repo, num_analyses_entity, str(num_correct_repo / num_analyses_repo),
                     str(num_correct_entity / num_analyses_entity), str(repos_with_error), str(repos_with_error_entity)])

print("Accuracy (repo): " + str(num_correct_repo) + " out of " + str(num_analyses_repo) +
      ". Num errors = " + str(num_error_repo) + ". " + str(num_correct_repo / num_analyses_repo))


print("Accuracy (entities): " + str(num_correct_entity) + " out of " + str(num_analyses_entity) +
      ". Num errors = " + str(num_error_entity) + ". " + str(num_correct_entity / num_analyses_entity))
