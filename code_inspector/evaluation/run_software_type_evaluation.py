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


def get_precision_from_confusion_matrix(software_type, confusion_matrix):
    # value / sum of row
    precision = confusion_matrix[software_type.value][software_type.value] / sum(confusion_matrix[software_type.value])
    return precision


def get_recall_from_confusion_matrix(software_type, confusion_matrix):
    # value / sum of column
    sum_column = 0
    for i in range(len(confusion_matrix)):
        sum_column += confusion_matrix[i][software_type.value]
    recall = confusion_matrix[software_type.value][software_type.value] / sum_column
    return recall


def print_confusion_matrix(confusion_matrix):
    print("Confusion matrix: ")
    print("Predicted \\ Annotated labels")
    print("\t\tpackage, library, service, script")
    for x in range(len(confusion_matrix)):
        print(SoftwareTypes(x).name, end=': ')
        for y in range(len(confusion_matrix)):
            print(confusion_matrix[x][y], end='')
            print(' ', end='')
        print()


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
    num_repos = 0
    for dir_name in os.listdir(repo_path):
        print("######## Processing: " + dir_name)  # repo_path
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
                    repos_with_error.append(dir_name)
                else:
                    confusion_matrix[type_predicted.value][type_benchmark.value] += 1
                    # If they are not the same, we annotate the error
                    if type_predicted != type_benchmark:
                        repos_with_error.append(dir_name)
                flag = 1
                num_repos += 1
        if not flag:
            print("--> ATTENTION! %s NOT FOUND in CSV (may not be a problem) " % dir_name)

    # Print confusion matrix
    print_confusion_matrix(confusion_matrix)

    # Create evaluation_summary.
    write_header = False
    if not os.path.exists(benchmark_summary):
        write_header = True

    with open(benchmark_summary, 'a') as summary:
        writer = csv.writer(summary, delimiter=',')
        if write_header:
            writer.writerow(
                ['date', '#repositories',
                 'precision_package', 'recall_package',
                 'precision_library', 'recall_library',
                 'precision_service', 'recall_service',
                 'precision_script', 'recall_script',
                 'precision_avg', 'recall_avg',
                 'errors'])
        date = datetime.now().strftime("%d/%m/%Y %H:%M:%S")
        p_package = get_precision_from_confusion_matrix(SoftwareTypes.Package, confusion_matrix)
        r_package = get_recall_from_confusion_matrix(SoftwareTypes.Package, confusion_matrix)
        p_library = get_precision_from_confusion_matrix(SoftwareTypes.Library, confusion_matrix)
        r_library = get_recall_from_confusion_matrix(SoftwareTypes.Library, confusion_matrix)
        p_service = get_precision_from_confusion_matrix(SoftwareTypes.Service, confusion_matrix)
        r_service = get_recall_from_confusion_matrix(SoftwareTypes.Service, confusion_matrix)
        p_script = get_precision_from_confusion_matrix(SoftwareTypes.Script, confusion_matrix)
        r_script = get_recall_from_confusion_matrix(SoftwareTypes.Script, confusion_matrix)
        p_avg = (p_package + p_library + p_service + p_script) / 4
        r_avg = (r_package + r_library + r_service + r_script) / 4
        writer.writerow([date, num_repos,
                         p_package, r_package,
                         p_library, r_library,
                         p_service, r_library,
                         p_script, r_script,
                         p_avg, r_avg, repos_with_error
                         ])

    # Second evaluation: Ranking
    # TO DO


if __name__ == "__main__":
    main()
    # minitest
    # matrix = [[17, 0, 0, 0],
    #           [5, 28, 0, 1],
    #           [0, 0, 15, 1],
    #           [1, 0, 0, 28]]
    # print_confusion_matrix(matrix)
    # print(get_precision_from_confusion_matrix(SoftwareTypes.Script, matrix))
