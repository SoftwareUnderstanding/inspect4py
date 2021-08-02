import csv
import os
import subprocess
import json
import pandas as pd
from datetime import datetime
import enum


class SoftwareTypes(enum.Enum):
    Package = 0
    Library = 1
    Service = 2
    Script = 3
    Error = 4


def return_type(string_with_type):
    if "package" in string_with_type:
        return SoftwareTypes.Package
    if "library" in string_with_type:
        return SoftwareTypes.Library
    if "service" in string_with_type:
        return SoftwareTypes.Service
    if "script" in string_with_type:
        return SoftwareTypes.Script
    return SoftwareTypes.Error


def main():
    # TODO: These should be configured separately, or set by input
    repo_path = "../../../test_repos/"
    benchmark_path = "../../evaluation/software_type/software_type_benchmark.csv"
    benchmark_summary = "../../evaluation/software_type/evaluation_summary.csv"

    benchmark_df = pd.read_csv(benchmark_path)

    confusion_matrix = [[0 for x in range(4)] for x in range(4)]

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

    repos_with_error = []
    for dir_name in os.listdir(repo_path):
        print("######## Processing: " + dir_name) # repo_path
        cmd = 'code_inspector -i ' + repo_path + dir_name + " -o ../../output_dir/ -si"
        proc = subprocess.Popen(cmd.encode('utf-8'), shell=True, stdin=subprocess.PIPE,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        stdout, stderr = proc.communicate()
        if not os.path.exists("../../output_dir/directory_info.json"):
            print("Error when applying code_inspector to " + dir_name + str(stderr))
            repos_with_error.append(dir_name)
            continue
        with open("../../output_dir/directory_info.json", "r") as file:
            data = json.load(file)
        file.close()
        # delete last DirInfo to avoid reading incorrect information in case of errors.
        os.remove("../../output_dir/directory_info.json")
        current_type = ""
        if 'software_type' in data.keys() and data['software_type']:
            current_type = data['software_type']

        flag = 0
        for index, row in benchmark_df.iterrows():
            if dir_name == row["repository"].split("/")[-1].strip():
                type_benchmark = return_type(row["label"].strip())
                type_predicted = return_type(current_type)
                print("Label: %s; Predicted: %s" % (type_benchmark, type_predicted))
                # fill confusion matrix
                if type_predicted == SoftwareTypes.Error or type_benchmark == SoftwareTypes.Error:
                    print("---> ERROR extracting type for %s" % dir_name)
                else:
                    confusion_matrix[type_predicted.value][type_benchmark.value] += 1
                flag = 1
        if not flag:
            print("--> ATTENTION! %s NOT FOUND in CSV (may not be a problem) " % dir_name)

    # Create evaluation_summary.
    write_header = False
    if not os.path.exists(benchmark_summary):
        write_header = True

    # Print confusion matrix
    print("Predicted/Benchmark")
    for x in range(4):
        for y in range(4):
            print(confusion_matrix[x][y], sep='')
        print("\n")

    # TODO @dgarijo: print precision and recall for each category
    # TODO @dgarijo: print overall precision and recall
    # TODO @dgarijo: add it to a new csv.
    

if __name__ == "__main__":
    main()
